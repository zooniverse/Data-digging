#Python 2.7.9 (default, Apr  5 2015, 22:21:35)
# full env in environment.yml
import sys, os

'''

This is a full aggregation of the Pulsar Hunters project, including user weighting.

Note it's quite a simple project - basically one Yes/No question - and there is gold-standard data, so the weighting is relatively straightforward and the aggregation is just determining a single fraction for each subject.

For an example of an aggregation of a much more complex question tree, check out scripts for Galaxy Zoo. The user weighting in that project is also completely different.

Hopefully this is well-enough commented below to be useful for others.
--BDS

'''


# file with raw classifications (csv) needed
# put this way up here so if there are no inputs we exit quickly before even trying to load everything else
try:
    classfile_in = sys.argv[1]
except:
    #classfile_in = 'pulsar-hunters-classifications_first500k.csv'
    # just a shout-out to whoever changed Panoptes so that the export filenames
    # are human-readable instead of their previous format. Thank you
    #classfile_in = 'data/2e3d12a2-56ca-4d1f-930a-9ecc7fd39885.csv'
    print("\nUsage: %s classifications_infile [weight_class aggregations_outfile]" % sys.argv[0])
    print("      classifications_infile is a Zooniverse (Panoptes) classifications data export CSV.")
    print("      weight_class is 1 if you want to calculate and apply user weightings, 0 otherwise.")
    print("      aggregations_outfile is the name of the file you want written. If you don't specify,")
    print("          the filename is %s by default." % outfile_default)
    sys.exit(0)


import numpy as np  # using 1.10.1
import pandas as pd  # using 0.13.1
#import datetime
#import dateutil.parser
import json


############ Define files and settings below ##############

# default outfile
outfile_default = 'pulsar_aggregations.csv'
rankfile_stem = 'subjects_ranked_by_weighted_class_asof_'

# file with tags left in Talk, for value-added columns below
talk_export_file = "helperfiles/project-764-tags_2016-01-15.json"

# file with master list between Zooniverse metadata image filename (no source coords) and
# original filename with source coords and additional info
# also I get to have a variable that uses "filename" twice where each means a different thing
# a filename for a file full of filenames #alliterationbiyotch
filename_master_list_filename = "helperfiles/HTRU-N_sets_keys.csv"

# this is a list of possible matches to known pulsars that was done after the fact so they
# are flagged as "cand" in the database instead of "known" etc.
poss_match_file = 'helperfiles/PossibleMatches.csv'


# later we will select on tags by the project team and possibly weight them differently
# note I've included the moderators and myself (though I didn't tag anything).
# Also note it's possible to do this in a more general fashion using a file with project users and roles
# However, hard-coding seemed the thing to do given our time constraints (and the fact that I don't think
# you can currently export the user role file from the project builder)
project_team = 'bretonr jocelynbb spindizzy Simon_Rookyard Polzin cristina_ilie jamesy23 ADCameron Prabu walkcr roblyon chiatan llevin benjamin_shaw bhaswati djchampion jwbmartin bstappers ElisabethB Capella05 vrooje'.split()

# define the active workflow - we will ignore all classifications not on this workflow
# we could make this an input but let's not get too fancy for a specific case.

# for beta test
#active_workflow_id = 1099
#active_workflow_major = 6

# for live project
active_workflow_id = 1224
active_workflow_major = 4

# do we want sum(weighted vote count) = sum(raw vote count)?
normalise_weights = True


# do we want to write an extra file with just classification counts and usernames
# (and a random color column, for treemaps)?
counts_out = True
counts_out_file = 'class_counts_colors.csv'





############ Set the other inputs now ###############


try:
    apply_weight = int(sys.argv[2])
except:
    apply_weight = 0

try:
    outfile = sys.argv[3]
except:
    outfile = outfile_default



#################################################################################
#################################################################################
#################################################################################
# This is the function that actually does the aggregating

def aggregate_class(grp):
    # translate the group to a dataframe because FML if I don't (some indexing etc is different)
    thegrp = pd.DataFrame(grp)

    # figure out what we're looping over below
    answers = thegrp.pulsar_classification.unique()

    # aggregating is a matter of grouping by different answers and summing the counts/weights
    byans = thegrp.groupby('pulsar_classification')
    ans_ct_tot = byans['count'].aggregate('sum')
    ans_wt_tot = byans['weight'].aggregate('sum')

    # we want fractions eventually, so we need denominators
    count_tot    = np.sum(ans_ct_tot) # we could also do len(thegrp)
    weight_tot   = np.sum(ans_wt_tot)

    # okay, now we should have a series of counts for each answer, one for weighted counts, and
    # the total votes and weighted votes for this subject.
    # now loop through the possible answers and create the raw and weighted vote fractions
    # and save the counts as well.

    # this is a list for now and we'll make it into a series and order the columns later
    class_agg = {}
    class_agg['count_unweighted'] = count_tot
    class_agg['count_weighted']   = weight_tot
    class_agg['subject_type']     = thegrp.subject_type.unique()[0]
    class_agg['filename']         = thegrp.filename.unique()[0]

    for a in answers:
        # don't be that jerk who labels things with "p0" or otherwise useless internal indices.
        # Use the text of the response next to this answer choice in the project builder (but strip spaces)
        raw_frac_label  = ('p_'+a).replace(' ', '_')
        wt_frac_label   = ('p_'+a+'_weight').replace(' ', '_')

        class_agg[raw_frac_label] = ans_ct_tot[a]/float(count_tot)
        class_agg[wt_frac_label]  = ans_wt_tot[a]/float(weight_tot)

    # oops, this is hard-coded so that there's Yes and No as answers - sorry to those trying to generalise
    col_order = ["filename", "p_Yes", "p_No", "p_Yes_weight", "p_No_weight",
                 "count_unweighted", "count_weighted", "subject_type"]

    return pd.Series(class_agg)[col_order]





#################################################################################
#################################################################################
#################################################################################

# The new weighting assignment function allows the user to choose between different weighting schemes
# though note the one in this function is not preferred for reasons explained below.
def assign_weight_old(seed):
    # keep the two seed cases separate because we might want to use a different base for each
    if seed < 0.:
        return max([0.05, pow(1.0025, seed)])
    elif seed > 0:
        return min([3.0, pow(1.0025, seed)])
    else:
        return 1.0


# assigns a weight based on a seed parameter
# The weight is assigned using the seed as an exponent and the number below as the base.
# The number is just slightly offset from 1 so that it takes many classifications for
# a user's potential weight to cap out at the max weight (3) or bottom out at the min (0.05).
# Currently there are 641 "known" pulsars in the DB so the base of 1.025 is largely based on that.
# Update: there are now about 5,000 simulated pulsars in the subject set as well, and they have a
# much higher retirement limit, so that more people will have classified them and we have more info.

# Note I'd rather this did a proper analysis with a confusion matrix etc but under a time crunch
# we went with something simpler.

def assign_weight(q, which_weight):

    # the floor weight for the case of which_weight == 2
    # i.e. someone who has seed = 0 will have this
    # seed = 0 could either be equal numbers right & wrong, OR that we don't have any information
    c0 = 0.5

    seed         = q[1].seed
    n_gs         = q[1].n_gs

    # Two possible weighting schemes:
    # which_weight == 1: w = 1.0025^(seed), bounded between 0.05 and 3.0
    # which_weight == 2: w = (1 + log n_gs)^(seed/n_gs), bounded between 0.05 and 3.0
    #
    # Weighting Scheme 1:
    # this is an okay weighting scheme, but it doesn't account for the fact that someone might be prolific
    # but not a very good classifier, and those classifiers shouldn't have a high weight.
    # Example: Bob does 10000 gold-standard classifications and gets 5100 right, 4900 wrong.
    # In this weighting scheme, Bob's weighting seed is +100, which means a weight of 1.0025^100 = 1.3,
    # despite the fact that Bob's classifications are consistent with random within 1%.
    # The weighting below this one would take the weight based on 100/10000, which is much better.
    if which_weight == 1:
        # keep the two seed cases separate because we might want to use a different base for each
        if seed < 0.:
            return max([0.05, pow(1.0025, seed)])
        elif seed > 0:
            return min([3.0, pow(1.0025, seed)])
        else:
            return 1.0

    elif which_weight == 2:
        if n_gs < 1: # don't divide by or take the log of 0
            # also if they didn't do any gold-standard classifications assume they have the default weight
            return c0
        else:
            # note the max of 3 is unlikely to be reached, but someone could hit the floor.
            return min([3.0, max([0.05, c0*pow((1.0 + np.log10(n_gs)), (float(seed)/float(n_gs)))])])

    else:
        # unweighted - so maybe don't even enter this function if which_weight is not 1 or 2...
        return 1.0

#################################################################################
#################################################################################
#################################################################################


# Get the Gini coefficient - https://en.wikipedia.org/wiki/Gini_coefficient
# Typical values of the Gini for healthy Zooniverse projects (Cox et al. 2015) are
#  in the range of 0.7-0.9.

def gini(list_of_values):
    sorted_list = sorted(list_of_values)
    height, area = 0, 0
    for value in sorted_list:
        height += value
        area += height - value / 2.
    fair_area = height * len(list_of_values) / 2
    return (fair_area - area) / fair_area



#################################################################################
#################################################################################
#################################################################################


# assign a color randomly if logged in, gray otherwise
def randcolor(user_label):
    if user_label.startswith('not-logged-in-'):
        # keep it confined to grays, i.e. R=G=B and not too bright, not too dark
        g = random.randint(25,150)
        return '#%02X%02X%02X' % (g,g,g)
        #return '#555555'
    else:
        # the lambda makes this generate a new int every time it's called, so that
        # in general R != G != B below.
        r = lambda: random.randint(0,255)
        return '#%02X%02X%02X' % (r(),r(),r())



#################################################################################
#################################################################################
#################################################################################
# These are functions that extract information from the various JSONs that are
# included in the classification exports. To Do: optimise these so that one .apply()
# call will extract them for everything without so many &^%@$ing loops.

def get_subject_type(q):
    try:
        return q[1].subject_json[q[1].subject_id]['#Class']
    except:
        return "cand"


def get_filename(q):
    try:
        return q[1].subject_json[q[1].subject_id]['CandidateFile']
    except:
        try:
            return q[1].subject_json[q[1].subject_id]['CandidateFileVertical']
        except:
            try:
                return q[1].subject_json[q[1].subject_id]['CandidateFileHorizontal']
            except:
                return "filenotfound.png"


# get number of gold-standard classifications completed by a user (used if weighting)
def get_n_gs(thegrp):
    return sum(pd.DataFrame(thegrp).seed != 0)


# Something went weird with IP addresses, so use more info to determine unique users
# Note the user_name still has the IP address in it if the user is not logged in;
# it's just that for this specific project it's not that informative.
def get_alternate_sessioninfo(row):

    # if they're logged in, save yourself all this trouble
    if not row[1]['user_name'].startswith('not-logged-in'):
        return row[1]['user_name']
    else:
        metadata = row[1]['meta_json']
        # IP + session, if it exists
        # (IP, agent, viewport_width, viewport_height) if session doesn't exist
        try:
            # start with "not-logged-in" so stuff later doesn't break
            return str(row[1]['user_name']) +"_"+ str(metadata['session'])
        except:
            try:
                viewport = str(metadata['viewport'])
            except:
                viewport = "NoViewport"

            try:
                user_agent = str(metadata['user_agent'])
            except:
                user_agent = "NoUserAgent"

            try:
                user_ip = str(row[1]['user_name'])
            except:
                user_ip = "NoUserIP"

            thesession = user_ip + user_agent + viewport
            return thesession


#################################################################################
#################################################################################
#################################################################################



# Print out the input parameters just as a sanity check
print("Computing aggregations using:")
print("   infile: %s" % classfile_in)
print("   weighted? %d" % apply_weight)
print("  Will print to %s after processing." % outfile)



#################################################################################
#################################################################################
#################################################################################
#
#
#
#
# Begin the main work
#
#
#
#
print("Reading classifications from %s ..." % classfile_in)

classifications = pd.read_csv(classfile_in) # this step can take a few minutes for a big file

# Talk tags are not usually huge files so this doesn't usually take that long
print("Parsing Talk tag file for team tags %s ..." % talk_export_file)
talkjson = json.loads(open(talk_export_file).read())
talktags_all = pd.DataFrame(talkjson)
# we only care about the Subject comments here, not discussions on the boards
# also we only care about tags by the research team & moderators
talktags = talktags_all[(talktags_all.taggable_type == "Subject") & (talktags_all.user_login.isin(project_team))].copy()
# make a username-tag pair column
# subject id is a string in the classifications array so force it to be one here or the match won't work
talktags['subject_id'] = [str(int(q)) for q in talktags.taggable_id]
talktags["user_tag"] = talktags.user_login+": #"+talktags.name+";"
# when we're talking about Subject tags, taggable_id is subject_id
talk_bysubj = talktags.groupby('subject_id')
# this now contains all the project-team-written tags on each subject, 1 row per subject
subj_tags = pd.DataFrame(talk_bysubj.user_tag.unique())
# if we need this as an explicit column
#subj_tags['subject_id'] = subj_tags.index


# likewise reading this matched files doesn't take long even though we have a for loop.
print("Reading master list of matched filenames %s..." % filename_master_list_filename)
matched_filenames = pd.read_csv(filename_master_list_filename)

print("Reading from list of possible matches to known pulsars %s..." % poss_match_file)
# ['Zooniverse name', 'HTRU-N name', 'Possible source']
possible_knowns = pd.read_csv(poss_match_file)
possible_knowns['is_poss_known'] = [True for q in possible_knowns['Possible source']]


# This section takes quite a while and it's because we have so many for loops, which I think is
# in part because reading out of a dict from a column in a DataFrame needs loops when done this way
# and in part because we were in a rush.
# I think it's possible we could pass this to a function and reshape things there, then return
# a set of new columns - but I didn't have time to figure that out under the deadlines we had.
print("Making new columns and getting user labels...")

# first, extract the started_at and finished_at from the annotations column
classifications['meta_json'] = [json.loads(q) for q in classifications.metadata]

classifications['started_at_str']  = [q['started_at']  for q in classifications.meta_json]
classifications['finished_at_str'] = [q['finished_at'] for q in classifications.meta_json]

# we need to set up a new user id column that's login name if the classification is while logged in,
# session if not (right now "user_name" is login name or hashed IP and, well, read on...)
# in this particular run of this particular project, session is a better tracer of uniqueness than IP
# for anonymous users, because of a bug with some back-end stuff that someone else is fixing
# but we also want to keep the user name if it exists, so let's use this function
#classifications['user_label'] = [get_alternate_sessioninfo(q) for q in classifications.iterrows()]
classifications['user_label'] = [get_alternate_sessioninfo(q) for q in classifications['user_name meta_json'.split()].iterrows()]

classifications['created_day'] = [q[:10] for q in classifications.created_at]

# Get subject info into a format we can actually use
classifications['subject_json'] = [json.loads(q) for q in classifications.subject_data]

'''
ALERT: I think they may have changed the format of the subject_dict such that later projects will have a different structure to this particular json.

That will mean you'll have to adapt this part. Sorry - but hopefully it'll use the format that I note below I wish it had, or something similarly simple.

'''

# extract the subject ID because that's needed later
# Note the subject ID becomes the *index* of the dict, which is actually pretty strange versus
# everything else in the export, and I'd really rather it be included here as "subject_id":"1234567" etc.
#
# You can isolate the keys as a new column but then it's a DictKey type, but stringifying it adds
# all these other characters that you then have to take out. Thankfully all our subject IDs are numbers
# this is a little weird and there must be a better way but... it works
classifications['subject_id'] = [str(q.keys()).replace("dict_keys(['", "").replace("'])", '') for q in classifications.subject_json]
# extract retired status, though not sure we're actually going to use it.
# also, what a mess - you have to extract the subject ID first and then use it to call the subject_json. UGH
# update: we didn't use it and each of these lines takes ages, so commenting it out
#classifications['retired'] = [q[1].subject_json[q[1].subject_id]['retired'] for q in classifications.iterrows()]


# Get annotation info into a format we can actually use
# these annotations are just a single yes or no question, yay
classifications['annotation_json'] = [json.loads(q) for q in classifications.annotations]
classifications['pulsar_classification'] = [q[0]['value'] for q in classifications.annotation_json]



# create a weight parameter but set it to 1.0 for all classifications (unweighted) - may change later
classifications['weight'] = [1.0 for q in classifications.workflow_version]
# also create a count parameter, because at the time of writing this .aggregate('count') was sometimes off by 1
classifications['count'] = [1 for q in classifications.workflow_version]


#######################################################
# discard classifications not in the active workflow  #
#######################################################
print("Picking classifications from the active workflow (id %d, version %d.*)" % (active_workflow_id, active_workflow_major))
# use any workflow consistent with this major version, e.g. 6.12 and 6.23 are both 6 so they're both ok
# also check it's the correct workflow id
the_active_workflow = [int(q) == active_workflow_major for q in classifications.workflow_version]
this_workflow = classifications.workflow_id == active_workflow_id
in_workflow = this_workflow & the_active_workflow
# note I haven't saved the full DF anywhere because of memory reasons, so if you're debugging:
# classifications_all = classifications.copy()
classifications = classifications[in_workflow]

print("Extracting filenames and subject types...")
# extract whether this is a known pulsar or a candidate that needs classifying - that info is in the
# "#Class" column in the subject metadata (where # means it can't be seen by classifiers).
# the options are "cand" for "candidate", "known" for known pulsar, "disc" for a pulsar that has been
# discovered by this team but is not yet published
# do this after you choose a workflow because #Class doesn't exist for the early subjects so it will break
# also don't send the entirety of classifications into the function, to save memory
#classifications['subject_type'] = [get_subject_type(q) for q in classifications.iterrows()]
#classifications['filename'] = [get_filename(q) for q in classifications.iterrows()]
classifications['subject_type'] = [get_subject_type(q) for q in classifications['subject_id subject_json'.split()].iterrows()]
classifications['filename'] = [get_filename(q) for q in classifications['subject_id subject_json'.split()].iterrows()]
# Let me just pause a second to rant again about the fact that subject ID is the index of the subject_json.
# Because of that, because the top-level access to that was-json-now-a-dict requires the subject id rather than
# just being label:value pairs, I have to do an iterrows() and send part of the entire classifications DF into
# a loop so that I can simultaneously access each subject ID *and* the dict, rather than just accessing the
# info from the dict directly, which would be much faster.



# this might be useful for a sanity check later
# first_class_day = min(classifications.created_day).replace(' ', '')
# last_class_day  = max(classifications.created_day).replace(' ', '')
# for some reason this is reporting last-classification dates that are days after the actual last
# classification. Not sure? Might be because this is a front-end reporting, so if someone has set
# their computer's time wrong we could get the wrong time here.
# could fix that by using created_at but ... I forgot.
last_class_time = max(classifications.finished_at_str)[:16].replace(' ', '_').replace('T', '_').replace(':', 'h')+"m"



## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## #
#######################################################
#         Apply weighting function (or don't)         #
#######################################################
## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## #

classifications['seed'] = [0 for q in classifications.weight]
classifications['is_gs'] = [0 for q in classifications.weight]

if apply_weight > 0:

    print("  Computing user weights...")

    # for now this is assuming all subjects marked as "known" or "disc" are pulsars
    # and also "fake" are simulated pulsars
    is_known = (classifications.subject_type == 'known') | (classifications.subject_type == 'disc') | (classifications.subject_type == 'fake')
    #is_candidate = np.invert(is_known)
    # if it's a non-gold-standard classification, mark it
    classifications.loc[is_known, 'is_gs'] = 1
    ok_incr   = 1.0  # upweight if correct
    oops_incr = -2.0 # downweight more if incorrect

    # find the correct classifications of known pulsars
    ok_class   = (is_known) & (classifications.pulsar_classification == 'Yes')

    # find the incorrect classifications of known pulsars
    oops_class = (is_known) & (classifications.pulsar_classification == 'No')

    # set the individual seeds
    classifications.loc[ok_class,   'seed'] = ok_incr
    classifications.loc[oops_class, 'seed'] = oops_incr

    # then group classifications by user name, which will weight logged in as well as not-logged-in (the latter by session)
    by_user = classifications.groupby('user_label')

    # get the user's summed seed, which goes into the exponent for the weight
    user_exp = by_user.seed.aggregate('sum')
    # then set up the DF that will contain the weights etc, and fill it
    user_weights = pd.DataFrame(user_exp)
    user_weights.columns = ['seed']
    user_weights['user_label'] = user_weights.index
    user_weights['nclass_user'] = by_user['count'].aggregate('sum')
    user_weights['n_gs'] = by_user['is_gs'].aggregate('sum')
    user_weights['weight'] = [assign_weight(q, apply_weight) for q in user_weights.iterrows()]
    #user_weights['weight'] = [assign_weight_old(q) for q in user_exp]

    # if you want sum(unweighted classification count) == sum(weighted classification count), do this
    if normalise_weights:
        user_weights.weight *= float(len(classifications))/float(sum(user_weights.weight * user_weights.nclass_user))

    # weights are assigned, now need to match them up to the main classifications table
    # making sure that this weight keeps the name 'weight' and the other gets renamed (suffixes flag)
    # if assign_weight == 0 then we won't enter this loop and the old "weights" will stay
    # as they are, i.e. == 1 uniformly.
    classifications_old = classifications.copy()
    classifications = pd.merge(classifications_old, user_weights, how='left',
                               on='user_label',
                               sort=False, suffixes=('_2', ''), copy=True)

else:
    # just make a collated classification count array so we can print it to the screen
    by_user = classifications.groupby('user_label')
    user_exp = by_user.seed.aggregate('sum')
    user_weights = pd.DataFrame(user_exp)
    user_weights.columns = ['seed']
    #user_weights['user_label'] = user_weights.index
    user_weights['nclass_user'] = by_user['count'].aggregate('sum')
    user_weights['n_gs'] = by_user['is_gs'].aggregate('sum')
    # UNWEIGHTED
    user_weights['weight'] = [1 for q in user_exp]





# grab basic stats
n_subj_tot  = len(classifications.subject_data.unique())
by_subject = classifications.groupby('subject_id')
subj_class = by_subject.created_at.aggregate('count')
all_users  = classifications.user_label.unique()
n_user_tot = len(all_users)
n_user_unreg = sum([q.startswith('not-logged-in-') for q in all_users])

# obviously if we didn't weight then we don't need to get stats on weights
if apply_weight > 0:
    user_weight_mean   = np.mean(user_weights.weight)
    user_weight_median = np.median(user_weights.weight)
    user_weight_25pct  = np.percentile(user_weights.weight, 25)
    user_weight_75pct  = np.percentile(user_weights.weight, 75)
    user_weight_min    = min(user_weights.weight)
    user_weight_max    = max(user_weights.weight)

nclass_mean   = np.mean(user_weights.nclass_user)
nclass_median = np.median(user_weights.nclass_user)
nclass_tot    = len(classifications)

user_weights.sort_values(['nclass_user'], ascending=False, inplace=True)


# If you want to print out a file of classification counts per user, with colors for making a treemap
# honestly I'm not sure why you wouldn't want to print this, as it's very little extra effort
if counts_out == True:
    print("Printing classification counts to %s..." % counts_out_file)
    user_weight['color'] = [randcolor(q) for q in user_weight.index]
    user_weight.to_csv(counts_out_file)



## ## ## ## ## ## ##             ## ## ## ## ## ## ## #
#######################################################
#            Print out basic project info             #
#######################################################
## ## ## ## ## ## ##             ## ## ## ## ## ## ## #

print("%d classifications from %d users, %d registered and %d unregistered.\n" % (nclass_tot, n_user_tot, n_user_tot - n_user_unreg, n_user_unreg))
print("Mean n_class per user %.1f, median %.1f." % (nclass_mean, nclass_median))
if apply_weight > 0:
    print("Mean user weight %.3f, median %.3f, with the middle 50 percent of users between %.3f and %.3f." % (user_weight_mean, user_weight_median, user_weight_25pct, user_weight_75pct))
    print("The min user weight is %.3f and the max user weight is %.3f.\n" % (user_weight_min, user_weight_max))
    cols_print = 'nclass_user weight'.split()
else:
    cols_print = 'nclass_user'
# don't make this leaderboard public unless you want to gamify your users in ways we already know
# have unintended and sometimes negative consequences. This is just for your information.
print("Classification leaderboard:")
print(user_weights[cols_print].head(20))
print("Gini coefficient for project: %.3f" % gini(user_weight['nclass_user']))



## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## #
#######################################################
# Aggregate classifications, unweighted and weighted  #
#######################################################
## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## #

print("\nAggregating classifications...\n")
class_agg = by_subject['weight count pulsar_classification subject_type filename'.split()].apply(aggregate_class)
# really ought to replace all the NaNs with 0.0


#######################################################
#                   Write to files                    #
#######################################################
#
# add value-added columns
#
# let people look up the subject on Talk directly from the aggregated file
class_agg['link'] = ['https://www.zooniverse.org/projects/zooniverse/pulsar-hunters/talk/subjects/'+str(q) for q in class_agg.index]
# after we do the merges below the new indices might not be linked to the subject id, so save it explicitly
class_agg['subject_id'] = [str(q) for q in class_agg.index]
# match up all the ancillary file data. Maybe there's a faster way to do this than with a chain but meh,
# it's actually not *that* slow compared to the clusterf*ck of for loops in the column assignment part above
class_agg_old = class_agg.copy()
class_agg_interm  = pd.merge(class_agg_old, subj_tags, how='left', left_index=True, right_index=True, sort=False, copy=True)
class_agg_interm2 = pd.merge(class_agg_interm,  matched_filenames, how='left', left_on='filename', right_on='Pulsar Hunters File', sort=False, copy=True)
class_agg         = pd.merge(class_agg_interm2, possible_knowns, how='left', left_on='filename', right_on='Zooniverse name', sort=False, copy=True)

# fill in the is_poss_known column with False where it is currently NaN
# currently it's either True or NaN -- with pd.isnull NaN becomes True and True becomes False, so invert that.
class_agg['is_poss_known'] = np.invert(pd.isnull(class_agg['is_poss_known']))

# make the list ranked by p_Yes_weight
class_agg.sort_values(['subject_type','p_Yes_weight'], ascending=False, inplace=True)


print("Writing aggregated output to file %s...\n" % outfile)
pd.DataFrame(class_agg).to_csv(outfile)

# Now make files ranked by p_Yes, one with all subjects classified and one with only candidates

# /Users/vrooje/anaconda/bin/ipython:1: FutureWarning: sort(columns=....) is deprecated, use sort_values(by=.....)
#   #!/bin/bash /Users/vrooje/anaconda/bin/python.app
#class_agg.sort('p_Yes_weight', ascending=False, inplace=True)
class_agg.sort_values(['p_Yes_weight'], ascending=False, inplace=True)

# I'd rather note the last classification date than the date we happen to produce the file
# rightnow = datetime.datetime.now().strftime('%Y-%M-%D_%H:%M')
# rankfile_all = rankfile_stem + rightnow + ".csv"
rankfile_all = 'all_'+rankfile_stem + last_class_time + ".csv"

# there go those hard-coded columns again
rank_cols = ['subject_id', 'filename', 'p_Yes_weight', 'count_weighted', 'p_Yes', 'count_unweighted', 'subject_type', 'link', 'user_tag', 'HTRU-N File']

print("Writing full ranked list to file %s...\n" % rankfile_all)
# write just the weighted yes percentage, the weighted count, the subject type, and the link to the subject page
# the subject ID is the index so it will be written anyway
pd.DataFrame(class_agg[rank_cols]).to_csv(rankfile_all)


rankfile = 'cand_allsubj_'+rankfile_stem + last_class_time + ".csv"
print("Writing candidate-only ranked list to file %s...\n" % rankfile)
# also only include entries where there were at least 5 weighted votes tallied
# and only "cand" subject_type objects
classified_candidate = (class_agg.count_weighted > 5) & (class_agg.subject_type == 'cand')
pd.DataFrame(class_agg[rank_cols][classified_candidate]).to_csv(rankfile)


rankfile_unk = 'cand_'+rankfile_stem + last_class_time + ".csv"
print("Writing candidate-only, unknown-only ranked list to file %s...\n" % rankfile_unk)
# also only include entries where there were at least 5 weighted votes tallied
# and only "cand" subject_type objects
classified_unknown_candidate = (classified_candidate) & (np.invert(class_agg.is_poss_known))
pd.DataFrame(class_agg[rank_cols][classified_unknown_candidate]).to_csv(rankfile_unk)

# copy the candidate list into Google Drive so others can see it, overwriting previous versions
# Note: this is the way I instantly shared the new aggregated results with collaborators, because
# Google Drive automatically syncs with the online version. Dropbox would work too, etc. YMMV
cpfile = "/Users/vrooje/Google Drive/pulsar_hunters_share/all_candidates_ranked_by_classifications_%dclass.csv" % nclass_tot
print("Copying to Google Drive folder as %s..." % cpfile)
os.system("cp -f '%s' '%s'" % (rankfile, cpfile))

# and the unknown candidate sub-list
cpfile2 = "/Users/vrooje/Google Drive/pulsar_hunters_share/unknown_candidates_ranked_by_classifications_%dclass.csv" % nclass_tot
print("Copying to Google Drive folder as %s..." % cpfile2)
os.system("cp -f '%s' '%s'" % (rankfile_unk, cpfile2))

# and just for the record, all subjects.
cpfile3 = "/Users/vrooje/Google Drive/pulsar_hunters_share/all_subjects_ranked_by_classifications_%dclass.csv" % nclass_tot
print("... and %s" % cpfile3)
os.system("cp -f '%s' '%s'" % (rankfile_all, cpfile3))

#done.
