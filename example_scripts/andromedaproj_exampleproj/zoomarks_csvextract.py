# -------------------------------------------------------------
# Panoptes Marking Export Script
#
# This script extracts individual markings from Zooniverse
# Panoptes classification data export CSV.  This script is 
# configured to export circular marker info for classifications
# collected only for the latest workflow version.
#
# Customizations are set for use with ap-aas229-test project.
# Column names, annotation info, and marking task ID may need
# be altered for this script to work for data exports from
# other projects.
#
# Written by: Cliff Johnson (lcj@ucsd.edu)
# Last Edited: 31 December 2016
# Based on scripts by Brooke Simmons 
# -------------------------------------------------------------

#Python 3.5.1
import sys

try:
    classfile_in = sys.argv[1]
    markfile_out = sys.argv[2]
except:
    print("\nUsage: "+sys.argv[0]+" classifications_infile markings_outfile")
    print("      classifications_infile: a Zooniverse (Panoptes) classifications data export CSV.")
    print("      markings_outfile: a CSV file with marking information from classifications.")
    print("\nExample: "+sys.argv[0]+" ap-aas229-test-classifications.csv ap-aas229-test-markings.csv")
    sys.exit(0)
#classfile_in = 'ap-aas229-test-classifications.csv'
#markfile_out = 'ap-aas229-test-markings.csv'

import pandas as pd
import json

# Read in classification CSV and expand JSON fields
classifications = pd.read_csv(classfile_in)
classifications['metadata_json'] = [json.loads(q) for q in classifications.metadata]
classifications['annotations_json'] = [json.loads(q) for q in classifications.annotations]
classifications['subject_data_json'] = [json.loads(q) for q in classifications.subject_data]

# Calculate number of markings per classification
# Note: index of annotations_json ("q" here) corresponds to task number (i.e., 0)
classifications['n_markings'] = [ len(q[0]['value']) for q in classifications.annotations_json ]

# Select only classifications from most recent workflow version
iclass = classifications[classifications.workflow_version == classifications['workflow_version'].max()]

# Output markings from classifications in iclass to new list of dictionaries (prep for pandas dataframe)
# Applicable for workflows with marking task as first task, and outputs data for circular markers (x,y,r)
clist=[]
for index, c in iclass.iterrows():
    if c['n_markings'] > 0:
        # Note: index of annotations_json corresponds to task number (i.e., 0)
        for q in c.annotations_json[0]['value']:
            
            # OPTIONAL EXPANSION: could use if statement here to split marker types
            
            clist.append({'classification_id':c.classification_id, 'user_name':c.user_name, 'user_id':c.user_id,
                          'created_at':c.created_at, 'subject_ids':c.subject_ids, 'tool':q['tool'], 
                          'tool_label':q['tool_label'], 'x':q['x'], 'y':q['y'], 'r':q['r'], 'frame':q['frame']})

# Output list of dictionaries to pandas dataframe and export to CSV.
col_order=['classification_id','user_name','user_id','created_at','subject_ids',
           'tool','tool_label','x','y','r','frame']
out=pd.DataFrame(clist)[col_order]
out.to_csv(markfile_out,index_label='mark_id')
