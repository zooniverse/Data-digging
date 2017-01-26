#Python 2.7.9 (default, Apr  5 2015, 22:21:35)
# the full environment I used to test this is in basic_project_stats.yml
import sys

# file with raw classifications (csv)
# put this way up here so if there are no inputs we exit quickly before even trying to load everything else
try:
    classfile_in = sys.argv[1]
except:
    print "\nUsage: "+sys.argv[0]+" classifications_infile"
    print "      classifications_infile is a Zooniverse (Panoptes) classifications data export CSV."
    print "\nAll output will be to stdout (about a paragraph worth).\n"
    sys.exit(0)



import numpy as np  # works in 1.10.1
import pandas as pd  # works in 0.13.1
#import datetime
#import dateutil.parser
import json





# columns currently in an exported Panoptes classification file:
# classification_id,user_name,user_id,user_ip,workflow_id,workflow_name,workflow_version,created_at,gold_standard,expert,metadata,annotations,subject_data

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
#       here we will ignore this too, except to count subjects once.
# we'll also ignore classification_id, user_ip, workflow information, gold_standard, and expert.
#
# some of these will be defined further down, but before we actually use this list.
#cols_used = ["created_at_ts", "user_name", "user_id", "created_at", "started_at", "finished_at"]


# Print out the input parameters just as a sanity check
print "Computing project stats using:"
print "   infile:",classfile_in




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


print "Reading classifications from "+classfile_in

classifications = pd.read_csv(classfile_in)

# first, extract the started_at and finished_at from the annotations column
classifications['meta_json'] = [json.loads(q) for q in classifications.metadata]


classifications['started_at_str']  = [q['started_at']  for q in classifications.meta_json]
classifications['finished_at_str'] = [q['finished_at'] for q in classifications.meta_json]

classifications['created_day'] = [q[:10] for q in classifications.created_at]

first_class_day = min(classifications.created_day).replace(' ', '')
last_class_day  = max(classifications.created_day).replace(' ', '')



# grab the subject counts
n_subj_tot  = len(classifications.subject_data.unique())
by_subject = classifications.groupby('subject_data')
subj_class = by_subject.created_at.aggregate('count')

# basic stats on how classified the subjects are
subj_class_mean = np.mean(subj_class)
subj_class_med  = np.median(subj_class)
subj_class_min  = np.min(subj_class)
subj_class_max  = np.max(subj_class)

# save processing time and memory in the groupby.apply(); only keep the columns we're going to use
#classifications = classifications[cols_used]

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
nclass_byuser_ranked.sort(ascending=False)

# very basic stats
nclass_med    = np.median(nclass_byuser)
nclass_mean   = np.mean(nclass_byuser)

# Gini coefficient - see the comments above the gini() function for more notes
nclass_gini   = gini(nclass_byuser)

print "\nOverall:\n\n",n_class_tot,"classifications of",n_subj_tot,"subjects by",n_users_tot,"classifiers,"
print n_reg,"registered and",n_unreg,"unregistered.\n"
print "That's %.2f classifications per subject on average (median = %.1f)." % (subj_class_mean, subj_class_med)
print "The most classified subject has ",subj_class_max,"classifications; the least-classified subject has",subj_class_min,".\n"
print "Median number of classifications per user:",nclass_med
print "Mean number of classifications per user: %.2f" % nclass_mean
print "\nTop 10 most prolific classifiers:\n",nclass_byuser_ranked.head(10)
print "\n\nGini coefficient for classifications by user: %.2f\n" % nclass_gini


# That's it. This program is very basic.
