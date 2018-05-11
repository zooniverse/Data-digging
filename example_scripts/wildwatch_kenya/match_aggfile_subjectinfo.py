import sys, os, glob
import pandas as pd, numpy as np
import ujson
import datetime
from ast import literal_eval

aggfile        = 'wildwatch-kenya-classifications-wf2030-wfid332.79_aggregated.csv'
subject_file   = 'wildwatch-kenya-subjects.csv'

workflow_id = 2030



try:
    aggfile = sys.argv[1]
except:
    print("Usage:\n%s aggfile\n  example aggregated classifications file: %s\n" % (sys.argv[0], aggfile))
    print("Optional inputs:")
    print("  subjects=projectname-subjects.csv (export from project builder)")
    print("  workflow_id=N")
    print("  outfile=filename.csv\n    file to save subject-matched aggregations to")
    print("    If you don't specify an outfile, the filename\n    will be based on the input aggfile name.")
    print("    If you vary the project from the suggested one above, you'll need to specify a subject file.\n")
    exit(0)

outfile      = aggfile.replace('.csv', '_subjmatched.csv')

# check for other command-line arguments
if len(sys.argv) > 2:
    # if there are additional arguments, loop through them
    for i_arg, argstr in enumerate(sys.argv[2:]):
        arg = argstr.split('=')

        if arg[0]   == "workflow_id":
            workflow_id = int(arg[1])
        elif (arg[0] == "outfile_match") | (arg[0] == "outfile"):
            outfile = arg[1]
        elif (arg[0] == "subjects") |  (arg[0] == "subj"):
            subject_file = arg[1]


# make sure you don't overwrite even if the input file doesn't end in .csv
if outfile == aggfile:
    outfile  = aggfile + '_subjmatched.csv'


# gets an index of a json in a DF cell
def get_loc(q, i):
    return q[i]

def get_name_origin(meta_row):
    row = meta_row[1].metadata_json
    ind = meta_row[0]
    passback = {"index": ind}
    # in theory if the data is well-formed this will always work
    try:
        passback["name"]   = row["name"]
        passback["origin"] = row["origin"]
    except:
        # in practice, some of the subjects were uploaded with manifests having no header rows,
        # so the first row of the manifest became the "header" and the column names are just wrong
        # still, it's generally an image file name and a directory of origin
        thename = "blank"
        theorigin = "blank"
        for k in row.keys():
            if ((row[k]).endswith(".jpg")) | ((row[k]).endswith(".jpeg")) | ((row[k]).endswith(".JPG")) | ((row[k]).endswith(".JPEG")):
                thename = row[k]
            else:
                theorigin = row[k]

        passback["name"]   = thename
        passback["origin"] = theorigin

    return passback



print(" Reading %s" % aggfile)

agg_all = pd.read_csv(aggfile)

# A lot of this is hard-coded to work for WWK specifically

print(" Reading %s" % subject_file)
subj_all = pd.read_csv(subject_file)

# subject files will have 1 row per (subject, workflow) pair so just pick the workflow we care about
# which means we'll get the retirement information correct as that's workflow-specific
subj_wf = subj_all[subj_all.workflow_id == workflow_id].copy()

# hard-coded: only include the first URL for each subject (ignore multiple images)
subj_wf['loc_json'] = [ujson.loads(q) for q in subj_wf.locations]
subj_wf['location'] = [get_loc(q, "0") for q in subj_wf.loc_json]

# don't include the locations jsons in the merging
subj_cols = 'subject_id project_id workflow_id subject_set_id metadata location classifications_count retired_at retirement_reason'.split()

print("  ... matching aggregations to subject info file ...")
agg_subj = pd.merge(agg_all, subj_wf[subj_cols], how="inner", left_on="subject_ids", right_on="subject_id", suffixes=("", "_2"))

print("  ... jailbreaking metadata ...")
# now try to break out the metadata
agg_subj['metadata_json'] = [ujson.loads(q) for q in agg_subj.metadata]
x = pd.DataFrame([get_name_origin(q) for q in agg_subj["subject_id metadata_json".split()].iterrows()])
x.set_index('index', inplace=True)
agg_subj["name"]   = x["name"]
agg_subj["origin"] = x["origin"]

out_cols = list(agg_subj.columns)
out_cols.remove('metadata_json')


agg_subj[out_cols].to_csv(outfile)
print("Printed subject-matched aggregations to %s." % outfile)
