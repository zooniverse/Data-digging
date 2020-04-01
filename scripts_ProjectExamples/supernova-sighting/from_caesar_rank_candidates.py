import sys, os, glob
import pandas as pd, numpy as np
import ujson
import datetime
from ast import literal_eval
from get_workflow_info import get_workflow_info, get_class_cols, translate_non_alphanumerics, get_short_slug
from flattenDict import flattenDict

# go from index numbers in the answer labels to the labels themselves,
# e.g. (0, 1) to ("Yes", "No")
def translate_store(the_store, workflow_answers):
    new_store = {}
    #print(the_store)
    # the index of the_store is very possibly strings e.g. '0', '1'
    for i_str in the_store.keys():
        # if blank answers are allowed the label won't be in the dictionary
        # so do it manually
        if i_str == '':
            new_store["Blank"] = the_store[i_str]
        else:
            thelabel = workflow_answers[int(i_str)]["label"]
            new_store[thelabel] = the_store[i_str]

    return new_store


# this is going to break if anything goes wrong
def translate_mostlikely(i_which, workflow_answers):
    return workflow_answers[int(i_which)]["label"]



def get_meta_cols(the_metadata):
    #print(the_metadata)
    col_vals = {}
    for thekey in the_metadata[1].keys():
        if thekey == 'subject_id':
            col_vals[thekey] = the_metadata[1][thekey]
        else:
            for metakey in the_metadata[1][thekey].keys():
                col_vals[metakey] = the_metadata[1][thekey][metakey]

    #return pd.Series(col_vals)
    return col_vals






#classfile_infile         = "supernova-sighting-classifications.csv"
subject_infile           = "supernova-sighting-subjects.csv"
#extract_infile           = "supernova-sighting-caesar-extract.csv"
reduction_infile         = "supernova-sighting-caesar-reduction.csv"
workflows_infile         = "supernova-sighting-workflows.csv"
workflow_contents_infile = "supernova-sighting-workflow_contents.csv"

reduction_outfile        = "supernova-sighting-caesar-reduction-withlabels.csv"

# if comparing to an old outfile
reduction_file_old       = "old/supernova-sighting-caesar-reduction-withlabels.csv"
# if not
#reduction_file_old       = ""

workflow_id      = 3638
workflow_version = 16.22

# get workflow info, particularly labels to answers in task T0
# (which is what we care about for this project)
workflow_df = pd.read_csv(workflows_infile)
workflow_cdf = pd.read_csv(workflow_contents_infile)
workflow_info = get_workflow_info(workflow_df, workflow_cdf, workflow_id, workflow_version)

# In [8]: workflow_info
# Out[8]:
# {u'T0': {u'answers': [{u'label': u'Yes',
#     'label_slug': u't0_is_there_a_candi___righthand_image_a0_yes',
#     u'next': u'T1'},
#    {u'label': u'No',
#     'label_slug': u't0_is_there_a_candi___righthand_image_a1_no',
#     u'next': u''}],
#   u'help': '',
#   u'question': u'Is there a candidate (a circular-like white spot) centered in the crosshairs of the left and right-hand image?',
#   'question_slug': u't0_is_there_a_candi___righthand_image',
#   u'required': True,
#   u'type': u'single'},
#  'first_task': 'T0',
#  'tasknames': [u'T0']}
#
# In [13]: workflow_info["T0"]["answers"][0]["label"]
# Out[13]: u'Yes'

reduction_raw = pd.read_csv(reduction_infile)

# In[16]: reduction_raw.columns

# Out[16]:
# Index([u'id', u'reducer_key', u'workflow_id', u'subject_id', u'created_at',
#       u'updated_at', u'subgroup', u'lock_version', u'store', u'expired',
#       u'data.most_likely', u'data.agreement', u'data.num_votes'],
#      dtype='object')

cols_in = reduction_raw.columns.values
cols_out = [w.replace('store', 'store_labeled').replace('data.most_likely', 'data.most_likely_labeled') for w in cols_in]

workflow_answers = workflow_info["T0"]["answers"]

reduction_raw['store_json'] = [ujson.loads(q) for q in reduction_raw['store']]
reduction_raw['store_labeled']  = [translate_store(q, workflow_answers) for q in reduction_raw['store_json']]

reduction_raw['data.most_likely_labeled'] = [translate_mostlikely(q, workflow_answers) for q in reduction_raw['data.most_likely']]



# read subjects and only keep rows relevant to this workflow and reduced dataset
subjects_all = pd.read_csv(subject_infile)
subjects = subjects_all[subjects_all.workflow_id == workflow_id].copy()
subject_ids_relevant = reduction_raw.subject_id.unique()
subjects_relevant    = subjects[subjects['subject_id'].isin(subject_ids_relevant)].copy()

# prep the metadata to be extracted into columns
subjects_relevant['metadata_json_flat'] = [flattenDict(ujson.loads(q)) for q in subjects_relevant.metadata]
subjects_relevant['image_url'] = [(ujson.loads(q))['0'] for q in subjects_relevant.locations]
meta_cols = pd.DataFrame([get_meta_cols(q) for q in subjects_relevant['subject_id metadata_json_flat'.split()].iterrows()])

# combine subjects with new columns, making sure to match on subject ID
subjects_meta = subjects_relevant.merge(meta_cols, on='subject_id', how='left', suffixes=('', '_2'))

# In [101]: subjects_meta.columns
# Out[101]:
# Index([           u'subject_id',            u'project_id',
#                  u'workflow_id',        u'subject_set_id',
#                     u'metadata',             u'locations',
#        u'classifications_count',            u'retired_at',
#            u'retirement_reason',    u'metadata_json_flat',
#                    u'image_url',           u'CandidateID',
#                         u'name'],
#       dtype='object')
#

meta_cols_out = subjects_meta.columns.values.tolist()
meta_cols_out.remove('metadata')
meta_cols_out.remove('metadata_json_flat')
meta_cols_out.remove('workflow_id')
meta_cols_out.remove('locations')

reduction_withsubj = reduction_raw[cols_out].merge(subjects_meta[meta_cols_out], how='left', on='subject_id', suffixes=('', '_2'))

reduction_withsubj['subj_link_zooniverse'] = ["https://www.zooniverse.org/projects/skymap/supernova-sighting/talk/subjects/%d" % q for q in reduction_withsubj.subject_id]

reduction_withsubj['skymapper_link'] = ["https://www.mso.anu.edu.au/skymapper/smt/transients/%s/" % q for q in reduction_withsubj.CandidateID]

reduction_withsubj.set_index('id', inplace=True)
reduction_withsubj.sort_values(['data.most_likely_labeled', 'data.agreement'], ascending=False, inplace=True)
#DataFrame.sort_values(by, axis=0, ascending=True, inplace=False, kind='quicksort', na_position='last')
reduction_withsubj.to_csv(reduction_outfile)

print("Output file written to %s ." % reduction_outfile)

# compare with earlier reduction and save a file with only subjects that have new information
if len(reduction_file_old) > 1:
    reductions_old = pd.read_csv(reduction_file_old)
    # if it only had a few classifications before let's still count it
    reductions_old_complete = reductions_old[reductions_old.classifications_count >= 20]
    subj_old = reductions_old_complete.subject_id.unique()
    reduction_new_withsubj = reduction_withsubj[np.invert(reduction_withsubj.subject_id.isin(subj_old))].copy()

    reduction_new_outfile = reduction_outfile.replace(".csv", "_NEWONLY.csv")
    # make sure you're not going to overwrite
    if reduction_outfile == reduction_new_outfile:
        reduction_new_outfile = "%s_NEWONLY.csv" % reduction_outfile

    reduction_new_withsubj.to_csv(reduction_new_outfile)

    print("Output file with ONLY NEW subjects written to %s ." % reduction_new_outfile)




#booya
