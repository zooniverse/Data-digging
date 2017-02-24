# -------------------------------------------------------------
# Panoptes Export Extraction Script
#
# This script extracts yes/no/null values for Steller Watch workflow 1
#
# Based on scripts by: Cliff Johnson (lcj@ucsd.edu)
# Last modified by LT: 2-27-17 
# -------------------------------------------------------------

# Note: In order for script to work, first needed to find-replace all null values with ""null"" within the original presence-or-absence-classifications-beta.csv file obtained from the Project Builder 'Data Exports'
# Code improvement would be to build in solution directly for this issue

#Python 3.5.2
import sys

try:
    classfile_in = sys.argv[1]
    extractfile_out = sys.argv[2]
except:
    print("\nUsage: "+sys.argv[0]+" classifications_infile extract_outfile")
    print("      classifications_infile: a Zooniverse (Panoptes) classifications data export CSV.")
    print("      markings_outfile: a CSV file with extracted information from classifications.")
    print("\nExample: "+sys.argv[0]+" test-classifications.csv test-extract.csv")
    sys.exit(0)
#classfile_in = 'presence-or-absence-classifications-beta.csv'
#extractfile_out = 'presence-or-absence-classifications-beta-extract.csv'

import pandas as pd
import json

# Read in classification CSV and expand JSON fields
classifications = pd.read_csv(classfile_in)
classifications['metadata_json'] = [json.loads(q) for q in classifications.metadata]
classifications['annotations_json'] = [json.loads(q) for q in classifications.annotations]
classifications['subject_data_json'] = [json.loads(q) for q in classifications.subject_data]

# Select only classifications from most recent workflow version
iclass = classifications[classifications.workflow_version == classifications['workflow_version'].max()]

clist=[]

for index, c in iclass.iterrows():
    clist.append({'classification_id':c.classification_id, 'user_name':c.user_name, 'user_id':c.user_id,'created_at':c.created_at, 'subject_ids':c.subject_ids, 'val':c.annotations_json[0]['value']})

            
# Output list of dictionaries to pandas dataframe and export to CSV.
col_order=['classification_id','user_name','user_id','created_at','subject_ids','val']
out=pd.DataFrame(clist)[col_order]
out.to_csv(extractfile_out,index_label='row_id')
