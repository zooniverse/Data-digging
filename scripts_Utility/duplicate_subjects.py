#!/usr/bin/env python

###################################
# Script: Duplicate Subjects
#
# To Use:
# 1) Edit input parameters below:
#    destination_subject_set_id = integer ID for destination subject set
#    input_subject_ids = list of integer subject IDs
#x
# 2) Run from command line: `python duplicate_subjects.py`

from panoptes_client import Panoptes, Subject, SubjectSet

###################################
# Input Parameters

puser = 'USERNAME'
ppswd = 'PASSWORD'
destination_project_id = 8749
destination_subject_set_id = 98117
input_subject_ids = [62834100, 62834101, 62834102, 62834103]

###################################

Panoptes.connect(username=puser, password=ppswd)

print('Processing {} subjects'.format(len(input_subject_ids)))

subjects = []
for sid in input_subject_ids:
    print('Working: Existing ID = {}'.format(sid))
    sub_in = Subject.find(sid)
    
    sub_out = Subject()
    sub_out.locations = sub_in.locations
    sub_out.links.project = destination_project_id
    sub_out.metadata = sub_in.metadata
    sub_out.save()
    
    subjects.append(sub_out)

print('Adding subjects to subject set {}'.format(destination_subject_set_id))
SubjectSet.find(destination_subject_set_id).add(subjects)
