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
#  - includes priority column 

file_subjects = 'example-subjects.csv'

###################################

# Read subjects from CSV
d = pd.read_csv(file_subjects)

Panoptes.connect(username=puser, password=ppswd)

# Iterate through subjects
for ind,row in d.iterrows():
    s = Subject.find(row.subject_id)
    # Note that without a second argument of subject_set_id, this will update the priority for all subject sets that the subject is in.
    s.update_priority(row['priority'])

