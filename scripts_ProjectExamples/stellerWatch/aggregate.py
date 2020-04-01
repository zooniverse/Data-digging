# -------------------------------------------------------------
# Panoptes Aggregation Script
#
# This script aggregates yes/no/null values for Steller Watch workflow 1
#
# Last modified by LT: 2-27-17 
# -------------------------------------------------------------

#Python 3.5.2

import sys
import pandas as pd
import numpy as np

try:
    classfile_in = sys.argv[1]
    aggfile_out = sys.argv[2]
except:
    sys.exit(0)


# Read in classification CSV
classifications = pd.read_csv(classfile_in)

# Define subject-ids and classification-result values

ids = classifications['subject_ids']
vals = classifications['val']

# Create unique list of subject-ids
uniq_ids = np.unique(ids)
num_uniq = uniq_ids.size

# Loop around each unique subject-id

num_classifications = []
frac_yes = []
frac_no = []
frac_null = []
agg_val = []

for index in range(len(uniq_ids)):

# Identify the indices for repeat classifications for that subject subject
    ind_mtch = np.where(ids == uniq_ids[index])[0]
    num_classifications.append(ind_mtch.size)

# Create array with all the classification results for that subject

    vals_mtch = vals[ind_mtch]

    ind_yes = np.where(vals_mtch == 'Yes!')
    ind_no = np.where(vals_mtch == 'No.')
    ind_null = np.where(vals_mtch == 'null')

# Determine the number of votes for each response type for that subject

    num_yes = ind_yes[0].size
    num_no = ind_no[0].size
    num_null = ind_null[0].size

#    print(ind_mtch)
#    print('# of classifications for this subject: ',ind_mtch[0].size)
#    print(vals_mtch)
#    print(ind_yes)
#    print('# of yes: ', num_yes, ', # of no: ', num_no, ', # of null: ',num_null)


# Determine the fraction of votes for each response type for that subject

    frac_yes_single = np.around( np.divide(num_yes,ind_mtch[0].size) ,decimals=3)
    frac_yes.append(frac_yes_single)
    frac_no_single = np.around( np.divide(num_no,ind_mtch[0].size) ,decimals=3)
    frac_no.append(frac_no_single)
    frac_null_single = np.around( np.divide(num_null,ind_mtch[0].size) ,decimals=3)
    frac_null.append(frac_null_single)

 
# Set the aggregate result (here based on vote with > 80% classifications) for that subject

    lim = 0.8

    if frac_yes_single >= lim:
        agg_val.append('Yes!')
    elif frac_no_single >= lim:
        agg_val.append('No.')
    elif frac_null_single >= lim:
        agg_val.append('null')
    else:
        agg_val.append('low confidence')


# End loop around each unique subject-Id


# Output results to csv

output = np.zeros(uniq_ids.size, dtype = [('subject_ids',object),('num_classifications',object),('frac_yes',object),('frac_no',object),('frac_null',object),('aggregate_result',object)])
output['subject_ids'] = uniq_ids
output['num_classifications'] = num_classifications
output['frac_yes'] = frac_yes
output['frac_no'] = frac_no
output['frac_null'] = frac_null
output['aggregate_result'] = agg_val

np.savetxt(aggfile_out, output, delimiter=',', fmt="%s", header = 'subject_ids,num_classifications,frac_yes,frac_no,frac_null,aggregate_result')
