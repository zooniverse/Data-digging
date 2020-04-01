import sys, os, glob
import pandas as pd, numpy as np
import ujson
import datetime
from get_workflow_info import get_workflow_info, translate_non_alphanumerics, get_short_slug
from aggregate_question_utils import breakout_anno_q, getfrac, aggregate_questions


# we've already used basic_project_stats.py to clean the file of duplicates and non-live classifications
infile = '/Users/vrooje/Documents/Astro/GalaxyZoo/bar_lengths/hubble_bar_lengths/galaxy-zoo-bar-lengths-classifications-barlengthmeas-wfids3_1422-liveonly-nodups.csv'


outfile_class = '/Users/vrooje/Documents/Astro/GalaxyZoo/bar_lengths/gzbl_project/galaxy-zoo-bar-lengths-classifications-nojson-wfids3_1422-liveonly-nodups.csv'
outfile_agg = '/Users/vrooje/Documents/Astro/GalaxyZoo/bar_lengths/gzbl_project/galaxy-zoo-bar-lengths-aggregated-classifications-wfids3_1422-liveonly-nodups.csv'

workflow_id = 3
workflow_version = 56.13

# get the workflow info
workflow_file  = '/Users/vrooje/Documents/Astro/GalaxyZoo/bar_lengths/gzbl_project/galaxy-zoo-bar-lengths-workflows.csv'
workflow_cfile = '/Users/vrooje/Documents/Astro/GalaxyZoo/bar_lengths/gzbl_project/galaxy-zoo-bar-lengths-workflow_contents.csv'

breakout_class = True


# check for other command-line arguments
if len(sys.argv) > 1:
    # if there are additional arguments, loop through them
    for i_arg, argstr in enumerate(sys.argv[1:]):
        arg = argstr.split('=')

        if arg[0]   == "workflow_id":
            workflow_id = int(arg[1])
        elif arg[0] == "workflow_version":
            workflow_version = float(arg[1])
        elif (arg[0] == "outfile_class"):
            outfile_class = arg[1]
        elif (arg[0] == "outfile_agg") | (arg[0] == "outfile"):
            outfile_agg = arg[1]
        elif (arg[0] == "workflows"):
            workflow_file = arg[1]
        elif (arg[0] == "workflow_contents"):
            workflow_cfile = arg[1]
        elif (arg[0] == "class_in") | (arg[0] == "classfile") | (arg[0] == "in_class"):
            infile = arg[1]
        elif arg[0] == "classfile_breakout":
            breakout_class = False
            classfile_breakout = arg[1]


workflow_df  = pd.read_csv(workflow_file)
workflow_cdf = pd.read_csv(workflow_cfile)
workflow_info = get_workflow_info(workflow_df, workflow_cdf, workflow_id, workflow_version)

# the default text for the question descriptions in the workflow_info is not that
# helpful because of the way our question text was written
# so, overwrite it - such that these concisely & uniquely identify the task
# note: this step isn't required to make the output columns unique because they
# will all have the task label attached - but it helps make the table more easily readable
workflow_info['init_shorttext'] = u'has_bar'
workflow_info['T1_shorttext']   = u'spiral_arms_attached'
workflow_info['T2_shorttext']   = u'ring_attached'
workflow_info['T3_shorttext']   = u'draw_bar_length_width'



if breakout_class:

    print("Reading classifications file %s ... %s" % (infile, datetime.datetime.now().strftime('%H:%M:%S')))
    classifications_all = pd.read_csv(infile, low_memory=False)

    classifications_all['anno_json'] = [ujson.loads(q) for q in classifications_all['annotations']]

else:
    # we don't need to do the work of breaking out, we just need to read the classifications file and
    # get the question dict

    print("Reading post-breakout classifications file %s ... %s" % (classfile_breakout, datetime.datetime.now().strftime('%H:%M:%S')))
    classifications_all = pd.read_csv(classfile_breakout, low_memory=False)

print("   ... %d total classifications in the file. Extracting workflow id %d v%s ..." % (len(classifications_all), workflow_id, str(workflow_version)))

in_workflow = (classifications_all.workflow_id == workflow_id) & (classifications_all.workflow_version.astype(int) == int(workflow_version))

classifications = classifications_all[in_workflow].copy()
index_label = 'classification_id'
classifications.set_index(index_label, inplace=True)

del classifications_all



print("Creating columns for this workflow...     %s" % datetime.datetime.now().strftime('%H:%M:%S'))
# get the columns we'll be adding and add the empty versions
#thecols = [index_label, 'subject_id', 'created_at', 'user_name', 'user_id', 'user_ip', 'metadata']
# add the column names from this workflow to the list.
thecols = []
theqcols = []
theqdict = {}
for i_task, task in enumerate(workflow_info['tasknames']):
    thecols.append(workflow_info[task+'_shorttext'])

    # we're really only concerned with question tasks for aggregation purposes
    if (workflow_info[task+'_type'] == 'single') | (workflow_info[task+'_type'] == 'multiple'):
        theqcols.append(workflow_info[task+'_shorttext'])
        theqdict[task] = workflow_info[task+'_shorttext']

    if breakout_class:
        # initialize the columns in the main table as well
        classifications[workflow_info[task+'_shorttext']] = np.empty(len(classifications.created_at), dtype=object)


# Also add tracking of np array indices
# we need this for the breakout_anno_q() function
# actually we don't anymore? but hey ho
d_cols = {}
for j in range(len(thecols)):
    d_cols[thecols[j]] = j

if breakout_class:
    print("Extracting question annotations...    %s" % datetime.datetime.now().strftime('%H:%M:%S'))
    # do it. Just... DO IT
    x = classifications.apply(lambda row: breakout_anno_q(row, workflow_info), axis=1)
    # the columns aren't always in the same order vs thecols list so just... force it?
    # there must be a better way here
    classifications[x.columns] = x

    # write the broken-out classifications to a file so that we can skip the earlier bit later if needed/desired
    # (not that I've written that in as an option yet or anything)
    classifications.to_csv(outfile_class)
    print("   copy of classifications file with extracted annotations written to %s" % outfile_class)


print("Beginning aggregation... %s" % datetime.datetime.now().strftime('%H:%M:%S'))
# now aggregate
# .apply('count') used to occasionally be off by 1, so I like to define a 'count'
# column and then .aggregate('sum') off that column instead.
# the benefit of this is that if the values of the 'count' column *aren't* all
# equal to 1, then the aggregation is doing a weighted sum with no extra work.
# it doesn't seem any slower except that you have to define this column.
classifications['count'] = np.ones_like(classifications.subject_ids, dtype=float)

class_counts = aggregate_questions(classifications, theqdict)

# write the aggregations
class_counts.to_csv(outfile_agg)

print("Aggregated %d classifications of %d subjects into %s   at %s" % (len(classifications), len(classifications.subject_ids.unique()), outfile_agg, datetime.datetime.now().strftime('%H:%M:%S')))




# for i, row in enumerate(classifications.iterrows()):
#     print("%d  %d" % (i, int((row[1]['subject_ids'].split(';'))[0])))
#     x = row[1]['anno_json']
#     print(x)
#     print("----\n")
#     if i >= 1:
#         break
#


#end
