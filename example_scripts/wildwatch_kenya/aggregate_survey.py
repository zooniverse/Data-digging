import sys, os, glob
import pandas as pd, numpy as np
import ujson
import datetime
from ast import literal_eval
from get_workflow_info import get_workflow_info, translate_non_alphanumerics, get_short_slug
from aggregate_question_utils import breakout_anno_survey, getfrac, aggregate_survey, write_class_row

classfile      = 'wildwatch-kenya-classifications_workflow_id2030_v321.78_nodups_inclnonlive.csv'
workflow_file  = 'wildwatch-kenya-workflows.csv'
workflow_cfile = 'wildwatch-kenya-workflow_contents.csv'

workflow_id = 2030
#workflow_version = "301.76"
workflow_version = "321.78"


try:
    classfile = sys.argv[1]
except:
    print("Usage:\n%s classfile\n  example classifications export file: %s\n" % (sys.argv[0], classfile))
    print("Optional inputs:")
    print("  workflows=projectname-workflows.csv (export from project builder)")
    print("  workflow_contents=projectname-workflow_contents.csv (export from project builder)")
    print("  workflow_id=N")
    print("  workflow_version=N  (looks like a number with format: major.minor)")
    print("  outfile_class=filename.csv\n    file to save exploded classifications with 1 annotation per row")
    print("  outfile_agg=filename.csv\n    file to save aggregated classifications")
    print("    If you don't specify an outfile_class or outfile_agg, the filenames\n    will be based on the input classfile name.")
    print("    If you vary the project from the suggested one above, you'll need to specify workflow files.\n")
    exit(0)

annofile     = classfile.replace('.csv', '_annotations_1lineeach.csv')
outfile      = classfile.replace('.csv', '_aggregated.csv')


# check for other command-line arguments
if len(sys.argv) > 2:
    # if there are additional arguments, loop through them
    for i_arg, argstr in enumerate(sys.argv[2:]):
        arg = argstr.split('=')

        if arg[0]   == "workflow_id":
            workflow_id = int(arg[1])
        elif arg[0] == "workflow_version":
            workflow_version = float(arg[1])
        elif (arg[0] == "outfile_class"):
            annofile = arg[1]
        elif (arg[0] == "outfile_agg") | (arg[0] == "outfile"):
            outfile = arg[1]
        elif (arg[0] == "workflows"):
            workflow_file = arg[1]
        elif (arg[0] == "workflow_contents"):
            workflow_cfile = arg[1]
        elif (arg[0] == "class_in") | (arg[0] == "classfile") | (arg[0] == "in_class"):
            infile = arg[1]
        elif arg[0] == "classfile_breakout":
            breakout_class = False
            classfile_breakout = arg[1]


# make sure you don't overwrite even if the input file doesn't end in .csv
if classfile == annofile:
    annofile = classfile + '_annotations_1lineeach.csv'

if   outfile == annofile:
    outfile  = classfile + '_aggregated.csv'

outfile_huge = outfile.replace('.csv', '_kitchensink.csv')

workflow_df  = pd.read_csv(workflow_file)
workflow_cdf = pd.read_csv(workflow_cfile)
workflow_info = get_workflow_info(workflow_df, workflow_cdf, workflow_id, workflow_version)

# print out some summary stuff so it's clear things have been read properly
print("Reading classifications from %s, aggregating workflow ID %d version %s, breaking out annotations into %s and saving aggregations into %s ..." % (classfile, workflow_id, workflow_version, annofile, outfile))

print(" NOTE: this program assumes every classification in the input classifications\nfile is from the major workflow version you're interested in.\n")
print("   If that is not the case, this program will crash.\n")
print("   The current best way to extract a single workflow's classifications from")
print("   the raw data export is to use basic_project_stats.py - check the comments\n   in this code for an example.")
#print("   > python ../basic_project_stats.py wildwatch-kenya-classifications.csv workflow_id=2030 workflow_version=321.78 outfile_csv=wildwatch-kenya-classifications_workflow_id2030_v321.78_nodups_inclnonlive.csv --remove_duplicates --keep_nonlive --keep_allcols \n")
#print("   substituting the file, workflow version and workflow id you need.")
#print("   the --keep_allcols flag is required if you want to aggregate from the\n   resulting file. The other flags are optional.")

try:
    classifications = pd.read_csv(classfile, low_memory=False)
except:
    classifications = pd.read_csv(classfile)

classifications['anno_json'] = [ujson.loads(q) for q in classifications.annotations]
classifications.fillna(0.0, inplace=True)

# now that we have the workflow information, we need to get the mark columns we will print
# we need both the survey ID columns and the "nothing here" etc. columns
thecols = []
for task in workflow_info['tasknames']:

    if workflow_info[task]['type'] == 'survey':
        # first, a column for what species was selected
        thecols.append(task.lower()+'_choice')
        # then columns for each request for additional sub-classification
        for question in workflow_info[task]['questionsOrder']:
            thecols.append("%s_%s" % (task.lower(), workflow_info[task]['questions'][question]['label_slug']))

    elif workflow_info[task]['type'] == 'shortcut':
        # each possible shortcut "answer" is a tickmark, i.e. True or False
        # so 1 col each
        for answer in workflow_info[task]['answers']:
            thecols.append(answer['label_slug'])

classcols = "classification_id subject_ids created_at user_name user_id user_ip".split()

printcols = classcols + thecols
theheader = {}
for i in range(len(printcols)):
    theheader[printcols[i]] = printcols[i]

# open the file
fp = open(annofile, "w")
# write the CSV header
write_class_row(fp, theheader, printcols)
# breakout and write each mark to the file
n_marks = classifications.apply(lambda row: breakout_anno_survey(row, workflow_info, fp, classcols, thecols), axis=1)
# done writing the file
fp.close()
print("%d annotations jailbroken from %d classifications, written to %s as individual marks..." % (sum(n_marks), len(classifications), annofile))

# save the number of marks per classification, in case it ends up being useful
classifications['n_marks'] = n_marks

print("Now reading in the jailbroken file and starting aggregation...")
# now re-read the csv file with the annotations
annotations = pd.read_csv(annofile)
annotations['count'] = np.ones_like(annotations.created_at)

# we need to group by subject in order to aggregate
by_subj = annotations.groupby('subject_ids')

class_agg = by_subj.apply(aggregate_survey, workflow_info=workflow_info)

print(" Aggregation done. Now checking which columns to print and printing... ")

# check for empty columns
all_cols = class_agg.columns.values
use_cols = (class_agg.columns.values).tolist()
for thecol in all_cols:
    if sum(class_agg[thecol]) == 0.0:
        use_cols.remove(thecol)

# write both the kitchen sink version and the version with no totally empty columns
class_agg.to_csv(outfile_huge)
class_agg[use_cols].to_csv(outfile)


print("\nAggregated classifications written to %s \n  (kitchen sink version: %s )\n" % (outfile, outfile_huge))


# to do:
# print a summary file, one line per subject, with all species idents for that subject

#end
