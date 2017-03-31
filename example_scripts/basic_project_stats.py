#Python 2.7.9 (default, Apr  5 2015, 22:21:35)
# the full environment I used to test this is in basic_project_stats.yml
import sys

# file with raw classifications (csv)
# put this way up here so if there are no inputs we exit quickly before even trying to load everything else
try:
    classfile_in = sys.argv[1]
except:
    print("\nUsage: %s classifications_infile" % sys.argv[0])
    print("      classifications_infile is a Zooniverse (Panoptes) classifications data export CSV.")
    print("  Optional inputs (no spaces):")
    print("    workflow_id=N")
    print("       specify the program should only consider classifications from workflow id N")
    print("    workflow_version=M")
    print("       specify the program should only consider classifications from workflow version M")
    print("       (note the program will only consider the major version, i.e. the integer part)")
    print("    --time_elapsed")
    print("       specify the program should compute classification durations and total classification work effort")
    print("\nAll output will be to stdout (about a paragraph worth).\n")
    sys.exit(0)



import numpy as np  # works in 1.10.1
import pandas as pd  # works in 0.13.1
import datetime
import dateutil.parser
import json
import gc

# default value is not to care about workflow ID or version
workflow_id      = -1
workflow_version = -1
# by default we won't worry about computing how much time effort the volunteers cumulatively spent
time_elapsed = False

# check for other command-line arguments
if len(sys.argv) > 2:
    # if there are additional arguments, loop through them
    for i_arg, argstr in enumerate(sys.argv[2:]):
        arg = argstr.split('=')

        if arg[0]   == "workflow_id":
            workflow_id = int(arg[1])
        elif arg[0] == "workflow_version":
            workflow_version = float(arg[1])
        elif arg[0] == "--time_elapsed":
            time_elapsed = True



# columns currently in an exported Panoptes classification file:
# classification_id,user_name,user_id,user_ip,workflow_id,workflow_name,workflow_version,created_at,gold_standard,expert,metadata,annotations,subject_data,subject_ids

# classification_id identifies the specific classification - should be unique for each row in this file
# user_name is either their registered name or "not-logged-in"+their hashed IP
# user_id is their numeric Zooniverse ID or blank if they're unregistered
# user_ip is a hashed version of their IP
# workflow_id is the numeric ID of this workflow, which you can find in the project builder URL for managing the workflow:
#       https://www.zooniverse.org/lab/[project_id]/workflow/[workflow_id]/
# workflow_name is the name you gave your workflow (for sanity checks)
# workflow_version is [bigchangecount].[smallchangecount] and is probably pretty big
# created_at is the date the entry for the classification was recorded
# gold_standard is 1 if this classification was done in gold standard mode
# expert is 1 if this classification was done in expert mode... I think
# metadata (json) is the data the browser sent along with the classification.
#       Includes browser information, language, started_at and finished_at
#       note started_at and finished_at are perhaps the easiest way to calculate the length of a classification
#       (the duration elapsed between consecutive created_at by the same user is another way)
#       the difference here is back-end vs front-end
# annotations (json) contains the actual classification information
#       which for this analysis we will ignore completely, for now
# subject_data is cross-matched from the subjects table and is for convenience in data reduction
# subject_ids has just the subject ids in the given classification
#       here we will ignore this too, except to count subjects once.
# we'll also ignore classification_id, user_ip, workflow information, gold_standard, and expert.
#


# Print out the input parameters just as a sanity check
print("Computing project stats using:")
print("   infile: %s" % classfile_in)




#################################################################################
#################################################################################
#################################################################################


# Get the Gini coefficient - https://en.wikipedia.org/wiki/Gini_coefficient
#
# The Gini coefficient measures inequality in distributions of things.
# It was originally conceived for economics (e.g. where is the wealth in a country?
#  in the hands of many citizens or a few?), but it's just as applicable to many
#  other fields. In this case we'll use it to see how classifications are
#  distributed among classifiers.
# G = 0 is a completely even distribution (everyone does the same number of
#  classifications), and ~1 is uneven (~all the classifications are done
#  by one classifier).
# Typical values of the Gini for healthy Zooniverse projects (Cox et al. 2015) are
#  in the range of 0.7-0.9.
#  That range is generally indicative of a project with a loyal core group of
#    volunteers who contribute the bulk of the classification effort, but balanced
#    out by a regular influx of new classifiers trying out the project, from which
#    you continue to draw to maintain a core group of prolific classifiers.
# Once your project is fairly well established, you can compare it to past Zooniverse
#  projects to see how you're doing.
#  If your G is << 0.7, you may be having trouble recruiting classifiers into a loyal
#    group of volunteers. People are trying it, but not many are staying.
#  If your G is > 0.9, it's a little more complicated. If your total classification
#    count is lower than you'd like it to be, you may be having trouble recruiting
#    classifiers to the project, such that your classification counts are
#    dominated by a few people.
#  But if you have G > 0.9 and plenty of classifications, this may be a sign that your
#    loyal users are -really- committed, so a very high G is not necessarily a bad thing.
#
# Of course the Gini coefficient is a simplified measure that doesn't always capture
#  subtle nuances and so forth, but it's still a useful broad metric.

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




# Begin the main stuff


print("Reading classifications from %s" % classfile_in)

#classifications = pd.read_csv(classfile_in)
# the above will work but uses a LOT of memory for projects with > 1 million
# classifications. Nothing here uses the actual classification data so don't read it
'''
If you are using this code on an older project, where the data export is from
before subject_ids were exported as their own column, change "subject_id" below
to "subject_data", and then when you define the groupby "by_subject" and count
subjects, you'll need to use subject_data instead of subject_ids.

Apologies for doing this, but subject_data contains the whole manifest so for
big projects with big catalogs it can take up a lot of memory, so we don't want to
use it if we don't have to.
'''
cols_keep = ["user_name", "user_id", "workflow_id", "workflow_version", "created_at", "metadata", "subject_ids"]
classifications = pd.read_csv(classfile_in, usecols=cols_keep)

# now restrict classifications to a particular workflow id/version if requested
if (workflow_id > 0) | (workflow_version > 0):

    # only keep the stuff that matches these workflow properties
    if (workflow_id > 0):

        print("Considering only workflow id %d" % workflow_id)

        in_workflow = classifications.workflow_id == workflow_id
    else:
        # the workflow id wasn't specified, so just make an array of true
        in_workflow = np.array([True for q in classifications.workflow_id])

    if (workflow_version > 0):

        classifications['version_int'] = [int(q) for q in classifications.workflow_version]

        print("Considering only major workflow version %d" % int(workflow_version))

        # we only care about the major workflow version, not the minor version
        in_version = classifications.version_int == int(workflow_version)
    else:
        in_version = np.array([True for q in classifications.workflow_version])


    if (sum(in_workflow & in_version) == 0):
        print("ERROR: your combination of workflow_id and workflow_version does not exist!\nIgnoring workflow id/version request and computing stats for ALL classifications instead.")
        #classifications = classifications_all
    else:
        # select the subset of classifications
        classifications = classifications[in_workflow & in_version]


else:
    # just use everything
    #classifications = classifications_all

    workflow_ids = classifications.workflow_id.unique()
    # this takes too much CPU time just for a print statement. Just use float versions
    #classifications['version_int'] = [int(q) for q in classifications.workflow_version]
    version_ints = classifications.workflow_version.unique()

    print("Considering all classifications in workflow ids:")
    print(workflow_ids)
    print(" and workflow_versions:")
    print(version_ints)



# first, extract the started_at and finished_at from the metadata column
classifications['meta_json'] = [json.loads(q) for q in classifications.metadata]

classifications['created_day'] = [q[:10] for q in classifications.created_at]

first_class_day = min(classifications.created_day).replace(' ', '')
last_class_day  = max(classifications.created_day).replace(' ', '')


# save processing time and memory in the groupby.apply(); only keep the columns we're going to use
cols_used = ["user_name", "user_id", "created_at", "created_day", "meta_json", "subject_ids"]
classifications = classifications[cols_used]
# collect() calls PyInt_ClearFreeList(), so explicitly helps free some active memory
gc.collect()

# grab the subject counts
n_subj_tot  = len(classifications.subject_ids.unique())
by_subject = classifications.groupby('subject_ids')
subj_class = by_subject.created_at.aggregate('count')

# basic stats on how classified the subjects are
subj_class_mean = np.mean(subj_class)
subj_class_med  = np.median(subj_class)
subj_class_min  = np.min(subj_class)
subj_class_max  = np.max(subj_class)

# free up some memory - note calling this does take CPU time but
# can free up GBs of active memory for big classification files
del by_subject
gc.collect()


# index by created_at as a timeseries
# note: this means things might not be uniquely indexed
# but it makes a lot of things easier and faster.
# update: it's not really needed in the main bit, but will do it on each group later.
#classifications.set_index('created_at_ts', inplace=True)


all_users = classifications.user_name.unique()
by_user = classifications.groupby('user_name')


# get total classification and user counts
n_class_tot = len(classifications)
n_users_tot = len(all_users)

unregistered = [q.startswith("not-logged-in") for q in all_users]
n_unreg = sum(unregistered)
n_reg   = n_users_tot - n_unreg

# for the leaderboard, which I recommend project builders never make public because
# Just Say No to gamification
# But it's still interesting to see who your most prolific classifiers are, and
# e.g. whether they're also your most prolific Talk users
nclass_byuser = by_user.created_at.aggregate('count')
nclass_byuser_ranked = nclass_byuser.copy()
nclass_byuser_ranked.sort_values(inplace=True, ascending=False)

# very basic stats
nclass_med    = np.median(nclass_byuser)
nclass_mean   = np.mean(nclass_byuser)

# Gini coefficient - see the comments above the gini() function for more notes
nclass_gini   = gini(nclass_byuser)

print("\nOverall:\n\n%d classifications of %d subjects by %d classifiers," % (n_class_tot,n_subj_tot,n_users_tot))
print("%d registered and %d unregistered.\n" % (n_reg,n_unreg))
print("That's %.2f classifications per subject on average (median = %.1f)." % (subj_class_mean, subj_class_med))
print("The most classified subject has %d classifications; the least-classified subject has %d.\n" % (subj_class_max,subj_class_min))
print("Median number of classifications per user: %.2f" %nclass_med)
print("Mean number of classifications per user: %.2f" % nclass_mean)
print("\nTop 10 most prolific classifiers:")
print(nclass_byuser_ranked.head(10))
print("\n\nGini coefficient for classifications by user: %.2f" % nclass_gini)
print("\nClassifications were collected between %s and %s.\n" % (first_class_day, last_class_day))


# if the input specified we should compute total time spent by classifiers, compute it
if time_elapsed:
    # free up some memory
    # do this inside the if because if we're not computing times then the program
    # is about to end so this memory will be freed up anyway
    del by_user
    gc.collect()


    classifications['started_at_str']  = [q['started_at'].replace('T',' ').replace('Z', '')  for q in classifications.meta_json]
    classifications['finished_at_str'] = [q['finished_at'].replace('T',' ').replace('Z', '') for q in classifications.meta_json]

    sa_temp = classifications['started_at_str']
    fa_temp = classifications['finished_at_str']

    #print("Creating timeseries...")#,datetime.datetime.now().strftime('%H:%M:%S.%f')


    try:
        classifications['started_at'] = pd.to_datetime(sa_temp, format='%Y-%m-%d %H:%M:%S.%f')
    except Exception as the_error:
        print("Oops:\n%s" % the_error)
        try:
            classifications['started_at'] = pd.to_datetime(sa_temp, format='%Y-%m-%d %H:%M:%S %Z')
        except Exception as the_error:
            print("Oops:\n%s" % the_error)
            classifications['started_at'] = pd.to_datetime(sa_temp)


    try:
        classifications['finished_at'] = pd.to_datetime(fa_temp, format='%Y-%m-%d %H:%M:%S.%f')
    except Exception as the_error:
        print("Oops:\n%s" % the_error)
        try:
            classifications['finished_at'] = pd.to_datetime(fa_temp, format='%Y-%m-%d %H:%M:%S %Z')
        except Exception as the_error:
            print("Oops:\n%s" % the_error)
            classifications['finished_at'] = pd.to_datetime(fa_temp)

    # we did all that above so that this would only take one line and be quite fast
    classifications['class_t_length'] = (classifications.finished_at - classifications.started_at)

    # throw away absurd time counts: accept lengths between 0 < dt < 30 minutes
    # anything outside that is either a wrongly reported time or the user walked away from their computer
    ok_times = (classifications.class_t_length > np.timedelta64(0, 's')) & (classifications.class_t_length < np.timedelta64(30, 'm'))

    # how many turned out to be okay?
    n_t_ok = sum(ok_times)

    # compute total times
    time_spent_classifying = np.sum(classifications['class_t_length'][ok_times])
    days_spent_classifying = time_spent_classifying / np.timedelta64(1, 'D')
    frac_good_durations = float(n_t_ok)/float(n_class_tot)

    print("Based on %d classifications (%.1f percent) where we can probably\ntrust the classification durations, the classifiers spent a total of %.2f days\n(or %.2f years) classifying in the project.\n" % (n_t_ok, frac_good_durations*100., days_spent_classifying, days_spent_classifying / 365.))

    mean_t_class   =   np.mean(classifications['class_t_length'][ok_times])
    median_t_class = np.median(classifications['class_t_length'][ok_times])

    human_effort_extrap = float(n_class_tot)*float(mean_t_class   / np.timedelta64(1, 'D')) / 365. # in years

    print("Mean classification length: %8.1f seconds"   % float(mean_t_class   / np.timedelta64(1, 's')))
    print("Median classification length: %6.1f seconds" % float(median_t_class / np.timedelta64(1, 's')))



    print("\nIf we use the mean to extrapolate and include the %.1f percent of\nclassifications where the reported duration had an error, that means\nthe total time spent is equivalent to %.2f years of human effort, or\n%.2f years of FTE (1 person working 40 hours/week, no holiday.)\n" % ((1-frac_good_durations)*100., human_effort_extrap, human_effort_extrap * (24.*7.)/40.))



#end
