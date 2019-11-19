#!/usr/bin/env python

###################################
# Script: Edit Metadata
#
# To Use:
# 1) Edit input parameters below.
# 2) Run from command line: `python edit_metadata.py`

from panoptes_client import Panoptes, SubjectSet

###################################
# Input Parameters

puser = 'USERNAME'
ppswd = 'PASSWORD'
subject_set_ids = [77172]
new_metadata = {"Attribution": "Photos are open source under a CC BY 3.0 license and were contributed to the project via CitSci.org."}

###################################

Panoptes.connect(username=puser, password=ppswd)

for ssid in subject_set_ids:
    subject_set = SubjectSet.find(ssid)

    print('Editing metadata for Subject Set #{0}: {1}'.format
          (subject_set.raw['id'], subject_set.raw['display_name']))

    for subject in subject_set.subjects:
        for key, value in new_metadata.items():
            subject.metadata[key]=value
        subject.save()
