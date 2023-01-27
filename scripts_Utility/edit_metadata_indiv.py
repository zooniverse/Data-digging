#!/usr/bin/env python

###################################
# Script: Edit Metadata
#
# To Use:
# 1) Edit input parameters below.
# 2) Run from command line: `python edit_metadata_indiv.py`

from panoptes_client import Panoptes, Subject
import pandas as pd

###################################
# Input Parameters

puser = 'USERNAME'
ppswd = 'PASSWORD'

# Subject Input File
#  - includes a `subject_id` column
#  - includes one column for each metadata field you wish to edit
#  - list each key to edit in meta_keys_to_edit list
file_subjects = 'infection-inspection-subjects.csv'
meta_keys_to_edit = ['#training_subject', '#feedback_1_id', '#feedback_1_answer']

###################################

# Read subjects from CSV
d = pd.read_csv(file_subjects)

Panoptes.connect(username=puser, password=ppswd)

# Iterate through subjects
for ind,row in d.iterrows():
    s = Subject.find(row.subject_id)
    for key in meta_keys_to_edit:
        s.metadata[key]=row[key]
    subject.save()
