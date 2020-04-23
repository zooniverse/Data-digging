#Python 2.7.9 (default, Apr  5 2015, 22:21:35)
# full env in environment.yml
import sys, os

'''

This is a full aggregation of the Exoplanet Explorers project, including user weighting.

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
    #classfile_in = 'exoplanet-explorers-classifications.csv'
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
import ujson
import random
import gc


############ Define files and settings below ##############

# default outfile
outfile_default = 'planet_aggregations.csv'
rankfile_stem = 'subjects_ranked_by_weighted_class_asof_'


# define the active workflow - we will ignore all classifications not on this workflow
# we could make this an input but let's not get too fancy for a specific case.

# for live project
active_workflow_id = 3821
active_workflow_major = 3

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
    answers = thegrp.planet_classification.unique()

    # aggregating is a matter of grouping by different answers and summing the counts/weights
    byans = thegrp.groupby('planet_classification')
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
    class_agg['candidate']        = thegrp.candidate.unique()[0]

    for a in answers:
        # ignore blank classifications
        if a is not None:
            # don't be that jerk who labels things with "p0" or otherwise useless internal indices.
            # Use the text of the response next to this answer choice in the project builder (but strip spaces)
            try:
                raw_frac_label  = ('p_'+a).replace(' ', '_')
                wt_frac_label   = ('p_'+a+'_weight').replace(' ', '_')
            except:
                # if we're here it's because all the classifications for this
                # subject are empty, i.e. they didn't answer the question, just
                # clicked done
                # in that case you're going to crash in a second, but at least
                # print out some information about the group before you do
                print("OOPS ")
                print(thegrp)
                print('-----------')
                print(a)
                print('+++++')
                print(ans_ct_tot,ans_wt_tot,count_tot,weight_tot)
                print('~~~~~~')
                print(answers)
                print(len(a))

            class_agg[raw_frac_label] = ans_ct_tot[a]/float(count_tot)
            class_agg[wt_frac_label]  = ans_wt_tot[a]/float(weight_tot)

    # oops, this is hard-coded so that there's Yes and No as answers - sorry to those trying to generalise
    col_order = ["candidate", "p_Yes", "p_No", "p_Yes_weight", "p_No_weight",
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

# Note I'd rather this did a proper analysis with a confusion matrix etc but under a time crunch
# we went with something simpler.

def assign_weight(q, which_weight):

    # the floor weight for the case of which_weight == 2 or 3
    # i.e. someone who has seed = 0 will have this
    # seed = 0 could either be equal numbers right & wrong, OR that we don't have any information
    c0 = 0.5

    seed         = q[1].seed
    n_gs         = q[1].n_gs

    # Three possible weighting schemes:
    # which_weight == 1: w = 1.0025^(seed), bounded between 0.05 and 3.0
    # which_weight == 2: w = (1 + log n_gs)^(seed/n_gs), bounded between 0.05 and 3.0
    # which_weight == 3: same as == 2 but the seed is different; see below
    #
    '''
    Weighting Scheme 1:
     this is an okay weighting scheme, but it doesn't account for the fact that someone might be prolific but not a very good classifier, and those classifiers shouldn't have a high weight.

     Example: Bob does 10000 gold-standard classifications and gets 5100 right, 4900 wrong. In this weighting scheme, Bob's weighting seed is +100, which means a weight of 1.0025^100 = 1.3, despite the fact that Bob's classifications are consistent with random within 1%.

     The weightings below this one would take the weight based on 100/10000, which is much better.
    '''
    if which_weight == 1:
        # keep the two seed cases separate because we might want to use a different base for each
        if seed < 0.:
            return max([0.05, pow(1.0025, seed)])
        elif seed > 0:
            return min([3.0, pow(1.0025, seed)])
        else:
            return 1.0

        '''
        Weighting Schemes 2 and 3:
         The passed seed is divided by the number of classifications.

         In weighting scheme 2, the seed has one fixed increment for correct classifications and another for incorrect classifications. It's a switch with two possible values: right, or wrong.

         Weighting scheme 3 is designed for projects where the gold-standards have variable intrinsic difficulty, so it sets the seed value for each gold-standard subject depending on how many people correctly classified it. Then it sums those individual seeds to the seed that's passed here and computes the weight in the same way as weighting scheme 2.
        '''

    elif (which_weight == 2) | (which_weight == 3):
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
# this is for making a treemap of your project's contributors
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
# included in the classification exports.
#
# To Do: optimise these so that one .apply() call will extract them for everything
# without so many &^%@$ing loops.

def get_subject_type(q):
    try:
        if q[1].subject_json[str(q[1].subject_ids)]['#sim'] == 'True':
            return True
        else:
            return False
    except:
        try:
            if q[1].subject_json[str(q[1].subject_ids)]['!sim'] == 'True':
                return True
            else:
                return False
        except:
            try:
                if q[1].subject_json[str(q[1].subject_ids)]['//sim'] == 'True':
                    return True
                else:
                    return False
            except:
                # if sim == False means it's a known non-planet,
                # we'll need to return something different for the case
                # where it's just not a sim
                return False


def get_filename(q):
    try:
        return q[1].subject_json[str(q[1].subject_ids)]['cand']
    except:
        try:
            return q[1].subject_json[str(q[1].subject_ids)]['plot']
        except:
            try:
                return q[1].subject_json[str(q[1].subject_ids)]['exofop']
            except:
                return "filenotfound.png"


# get number of gold-standard classifications completed by a user (used if weighting)
def get_n_gs(thegrp):
    return sum(pd.DataFrame(thegrp).seed != 0)


# Something went weird with IP addresses, so use more info to determine unique users
# Note the user_name still has the IP address in it if the user is not logged in;
# it's just that for this specific project it's not that informative.
# Note: the above was for Pulsar Hunters and IPs worked fine in Exoplanet Explorers
#   so we don't really need this, but keep it in case you ever want to try to identify
#   unique users based on something other than IP address
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






def get_live_project(meta_json):
    try:
        return meta_json['live_project']
    except:
        # apparently some subject metadata doesn't have this? dunno?
        return False


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

'''
 This section takes quite a while and it's because we have so many for loops, which I think is in part because reading out of a dict from a column in a DataFrame needs loops when done this way and in part because we were in a rush.

 I think it's possible we could pass this to a function and reshape things there, then return a set of new columns - but I didn't have time to figure that out under the deadlines we had.
'''
print("Making new columns and getting user labels...")

# first, extract the started_at and finished_at from the annotations column
classifications['meta_json'] = [ujson.loads(q) for q in classifications.metadata]

# discard classifications made when the project was not in Live mode
#
# would that we could just do q['live_project'] but if that tag is missing for
# any classifications (which it is in some cases) it crashes
classifications['live_project']  = [get_live_project(q) for q in classifications.meta_json]

# if this line gives you an error you've read in this boolean as a string
# so need to convert "True" --> True and "False" --> False
class_live = classifications[classifications.live_project].copy()
n_class_thiswf = len(classifications)
n_live = sum(classifications.live_project)
n_notlive = n_class_thiswf - n_live
print(" Removing %d non-live classifications..." % n_notlive)

# don't make a slice but also save memory
classifications = pd.DataFrame(class_live)
del class_live
gc.collect()

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





classifications['started_at_str']  = [q['started_at']  for q in classifications.meta_json]
classifications['finished_at_str'] = [q['finished_at'] for q in classifications.meta_json]

# we need to set up a new user id column that's login name if the classification is while logged in,
# session if not (right now "user_name" is login name or hashed IP and, well, read on...)
# in this particular run of this particular project, session is a better tracer of uniqueness than IP
# for anonymous users, because of a bug with some back-end stuff that someone else is fixing
# but we also want to keep the user name if it exists, so let's use this function
classifications['user_label'] = [get_alternate_sessioninfo(q) for q in classifications['user_name meta_json'.split()].iterrows()]

classifications['created_day'] = [q[:10] for q in classifications.created_at]

print("Getting subject info...")

# Get subject info into a format we can actually use
classifications['subject_json'] = [ujson.loads(q) for q in classifications.subject_data]

'''
ALERT: I think they may have changed the format of the subject_dict such that later projects will have a different structure to this particular json.

That will mean you'll have to adapt this part. Sorry - but hopefully it'll use the format that I note below I wish it had, or something similarly simple.

'''

print("Getting classification info...")

# Get annotation info into a format we can actually use
# these annotations are just a single yes or no question, yay
classifications['annotation_json'] = [ujson.loads(q) for q in classifications.annotations]
classifications['planet_classification'] = [q[0]['value'] for q in classifications.annotation_json]



# create a weight parameter but set it to 1.0 for all classifications (unweighted) - may change later
classifications['weight'] = [1.0 for q in classifications.workflow_version]
# also create a count parameter, because at the time of writing this .aggregate('count') was sometimes off by 1
classifications['count'] = [1 for q in classifications.workflow_version]



print("Extracting filenames and subject types...")

'''
 extract whether this is a known planet or a candidate that needs classifying - that info is in the "?sim" column in the subject metadata (where the ? can be either "#", "!" or "//").

 do this after you choose a workflow because #Class doesn't exist for the early subjects so it will break

 also don't send the entirety of classifications into the function, to save memory
'''
classifications['subject_type'] = [get_subject_type(q) for q in classifications['subject_ids subject_json'.split()].iterrows()]
classifications['candidate'] = [get_filename(q) for q in classifications['subject_ids subject_json'.split()].iterrows()]


# this might be useful for a sanity check later
# first_class_day = min(classifications.created_day).replace(' ', '')
# last_class_day  = max(classifications.created_day).replace(' ', '')
# for some reason this is reporting last-classification dates that are days after the actual last
# classification. Might be because this is a front-end reporting, so if someone has set
# their computer's time wrong we could get the wrong time here.
# could fix that by using created_at...
#last_class_time = max(classifications.finished_at_str)[:16].replace(' ', '_').replace('T', '_').replace(':', 'h')+"m"
last_class_time = max(classifications.created_at)[:16].replace(' ', '_').replace('T', '_').replace(':', 'h')+"m"




## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## #
#######################################################
#         Apply weighting function (or don't)         #
#######################################################
## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## #

classifications['seed'] = [0 for q in classifications.weight]
classifications['is_gs'] = [0 for q in classifications.weight]

if apply_weight > 0:

    print("  Computing user weights...")

    # if it breaks on this and gives a "str + int" error check these are
    # actually booleans and not just strings that say "True" or "False"
    # and note setting an array of those strings with a .astype(bool)
    # RETURNS True FOR ALL VALUES BECAUSE WHYYYYYYYYYY
    is_known = classifications.subject_type.values
    #is_candidate = np.invert(is_known)
    # if it's a non-gold-standard classification, mark it
    classifications.loc[is_known, 'is_gs'] = 1

    if apply_weight < 2:
        # the simple case of incrementing or decrementing the seed weight
        ok_incr   = 1.0  # upweight if correct
        # downweight only a tiny (constant) amount if users missed a sim
        oops_incr = -0.01
    else:
        # this will be scaled by how easy the sim is to spot
        # so this is the max upweight if ~all users missed it and one spotted it
        ok_incr   = 2.0
        # this is the max downweight if ~all users spotted it and one missed it
        oops_incr = -1.0
        '''
          I am really not convinced this is the right weighting scheme; it's probably worth testing various things out, including trying to make an actual confusion matrix.

          Well, it would be, if we had true negative sims. But we don't.
        '''

    # find the correct classifications of known planets
    ok_class   = (is_known) & (classifications.planet_classification == 'Yes')

    # find the incorrect classifications of known planets
    oops_class = (is_known) & (classifications.planet_classification == 'No')


    # if we're weighting differently based on how hard each particular sim is to spot
    # (measured by what fraction of people spotted it)
    # then we need to aggregate just the sims to get the unweighted fractions
    # and then update the seeds for those
    if apply_weight == 3:
        print("Weighting of sims based on sim difficulty (this takes longer)...")
        by_subj_sims = classifications[is_known].groupby('subject_ids')
        sims_agg = by_subj_sims['weight count planet_classification subject_type candidate'.split()].apply(aggregate_class)
        # replace NaN with 0.0
        sims_agg.fillna(value=0.0, inplace=True)

        '''
        we want to adjust the seed for each subject's weight based on what
        fraction of classifiers spotted the planet in the sim subject
        if we're weighting Alice's classification and Alice said Yes to a sim
        (i.e. got it right), but everyone else got it right too, then this
        subject doesn't give us much information about her ability, so the
        seed should be low. On the other hand, if she spotted it when most
        others missed it, she should get a nice upweight as a reward,
        so the multiplier for the ok_class group is actually p_No.
        likewise, if Bob failed to spot a sim but so did everyone else, then
        the sim is just impossible to spot and Bob shouldn't be penalized for
        that, whereas if everyone spotted it but Bob, Bob should be downweighted
        more heavily; so the multiplier for the oops_class group is p_Yes.

        We don't have true-negative sims, so if someone correctly spots a very
        difficult sim we can't tell whether they are really that astute or
        whether they're just really optimistic about transits.

        So this weighting scheme has the effect of rewarding the optimists with higher weightings, and I'm unconvinced that's the right way to go. After
        some spot checking I think it's at least possible we should be trying to
        get the false positive rate down a bit.

        Just noting that here.

        '''
        sims_agg['fseed_ok']   = sims_agg['p_No']
        sims_agg['fseed_oops'] = sims_agg['p_Yes']

        # now we have multipliers for each sim subject, add them back to the
        # classifications dataframe
        classifications_old = classifications.copy()
        classifications = pd.merge(classifications_old, sims_agg['fseed_ok fseed_oops'.split()], how='left', left_on='subject_ids', right_index=True, sort=False, suffixes=('_2', ''), copy=True)

        del classifications_old
        #classifications['fseed_ok fseed_oops'.split()].fillna(value=0.0, inplace=True)
        # set the individual seeds
        classifications.loc[ok_class,   'seed'] = ok_incr * classifications['fseed_ok'][ok_class]
        classifications.loc[oops_class, 'seed'] = oops_incr * classifications['fseed_oops'][oops_class]


    # then group classifications by user name, which will weight logged in as well as not-logged-in (the latter by session)
    by_user = classifications.groupby('user_label')

    # get the user's summed seed, which goes into the exponent for the weight
    user_exp = by_user.seed.aggregate('sum')
    # then set up the DF that will contain the weights etc, and fill it
    user_weights = pd.DataFrame(user_exp)
    user_weights.columns = ['seed']
    user_weights['user_label'] = user_weights.index
    user_weights['user_id'] = by_user['user_id'].head(1)
    user_weights['nclass_user'] = by_user['count'].aggregate('sum')
    user_weights['n_gs'] = by_user['is_gs'].aggregate('sum')
    user_weights['weight'] = [assign_weight(q, apply_weight) for q in user_weights.iterrows()]
    #user_weights['weight'] = [assign_weight_old(q) for q in user_exp]

    # if you want sum(unweighted classification count) == sum(weighted classification count), do this
    if normalise_weights:
        user_weights['weight_unnorm'] = user_weights['weight'].copy()
        user_weights.weight *= float(len(classifications))/float(sum(user_weights.weight * user_weights.nclass_user))

    # weights are assigned, now need to match them up to the main classifications table
    # making sure that this weight keeps the name 'weight' and the other gets renamed (suffixes flag)
    # if assign_weight == 0 then we won't enter this loop and the old "weights" will stay
    # as they are, i.e. == 1 uniformly.
    classifications_old = classifications.copy()
    classifications = pd.merge(classifications_old, user_weights, how='left',
                               on='user_label',
                               sort=False, suffixes=('_2', ''), copy=True)
    del classifications_old

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


gc.collect()



# grab basic stats
n_subj_tot  = len(classifications.subject_data.unique())
by_subject = classifications.groupby('subject_ids')
subj_class = by_subject.created_at.aggregate('count')
all_users  = classifications.user_label.unique()
n_user_tot = len(all_users)
n_user_unreg = sum([q.startswith('not-logged-in-') for q in all_users])
last_class_id = max(classifications.classification_id)

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
print("Gini coefficient for project: %.3f" % gini(user_weights['nclass_user']))



# If you want to print out a file of classification counts per user, with colors
# for making a treemap
# honestly I'm not sure why you wouldn't want to print this, as it's very little
# extra effort AND it's the only place we record the user weights
if counts_out == True:
    print("Printing classification counts to %s..." % counts_out_file)
    user_weights['color'] = [randcolor(q) for q in user_weights.index]
    user_weights.to_csv(counts_out_file)






## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## #
#######################################################
# Aggregate classifications, unweighted and weighted  #
#######################################################
## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## #

print("\nAggregating classifications...\n")
class_agg = by_subject['weight count planet_classification subject_type candidate'.split()].apply(aggregate_class)
# if p_Ans = 0.0 the function skipped those values, so replace all the NaNs with 0.0
class_agg.fillna(value=0.0, inplace=True)


#######################################################
#                   Write to files                    #
#######################################################
#
# add value-added columns
#
# let people look up the subject on Talk directly from the aggregated file
class_agg['link'] = ['https://www.zooniverse.org/projects/ianc2/exoplanet-explorers/talk/subjects/'+str(q) for q in class_agg.index]
# and provide the exofop link too
# the int(float(q)) thing is in case it reads as a string, which breaks int(q)
class_agg['exofop'] = ['https://exofop.ipac.caltech.edu/k2/edit_target.php?id=%d' % int(float(q)) for q in class_agg.candidate]
# after we do the merges below the new indices might not be linked to the subject id, so save it explicitly
class_agg['subject_ids'] = [str(q) for q in class_agg.index]

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
rankfile_all = 'all_%s_%s_lastid_%d.csv' % (rankfile_stem, last_class_time, last_class_id)

# there go those hard-coded columns again
#rank_cols = ['subject_ids', 'candidate', 'p_Yes_weight', 'count_weighted', 'p_Yes', 'count_unweighted', 'subject_type', 'link', 'user_tag', 'HTRU-N File']
rank_cols = ['subject_ids', 'candidate', 'p_Yes_weight', 'count_weighted', 'p_Yes', 'count_unweighted', 'subject_type', 'link']

print("Writing full ranked list to file %s...\n" % rankfile_all)
# write just the weighted yes percentage, the weighted count, the subject type, and the link to the subject page
# the subject ID is the index so it will be written anyway
pd.DataFrame(class_agg[rank_cols]).to_csv(rankfile_all)


rankfile = 'nonsim_allsubj_%s_%s_lastid_%d.csv' % (rankfile_stem, last_class_time, last_class_id)
print("Writing candidate-only ranked list to file %s...\n" % rankfile)
# also only include entries where there were at least 5 weighted votes tallied
# and only "cand" subject_type objects
classified_candidate = (class_agg.count_weighted > 5) & (class_agg.subject_type == False)
pd.DataFrame(class_agg[rank_cols][classified_candidate]).to_csv(rankfile)


# copy the candidate list into Google Drive so others can see it, overwriting previous versions
# Note: this is the way I instantly shared the new aggregated results with collaborators, because
# Google Drive automatically syncs with the online version. Dropbox would work too, etc. YMMV
cpfile = "/Users/vrooje/Google Drive/exoplanet_explorers_share/all_candidates_ranked_by_classifications_%dclass.csv" % nclass_tot
print("Copying to Google Drive folder as %s..." % cpfile)
os.system("cp -f '%s' '%s'" % (rankfile, cpfile))

# and just for the record, all subjects.
cpfile3 = "/Users/vrooje/Google Drive/exoplanet_explorers_share/all_subjects_ranked_by_classifications_%dclass.csv" % nclass_tot
print("... and %s" % cpfile3)
os.system("cp -f '%s' '%s'" % (rankfile_all, cpfile3))

#done.
