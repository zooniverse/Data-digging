""" This script is a demo for the flatten_classification_frame where it is used to slice out (or select)
 two specific subject numbers for the Aerobotany classification download.
 This script demonstrates shows the basic script modified in four ways:
 1) The actual path and file names were modified to match the files on my drive.
 2) The comment lines have been stripped out - This script is actually fairly short!
 3) Unused slice conditions have been deleted except for one we want which selects only two subject_ids.
 4) The output file field names and the writer line have been simplified by eliminating many of the fields
 that were not required to give us the info we wanted which was to determine if the retirement limit was
 met for these two subject numbers for a specific workflow (The output file showed that they were. -
 gold standard classifications done under a different workflow did NOT reduce the regular classification limit)"""

import csv
import json
import sys
from datetime import datetime

csv.field_size_limit(sys.maxsize)

location = r'C:\py\AAClass\amazon-aerobotany-classifications_2017-03-18.csv'
out_location = r'C:\py\AAClass\flatten_class_frame_demo_output.csv'


# define a function that returns True or False based on whether the argument record is to be included or not in
# the output file based on the conditional clauses.

def include(class_record):
    if int(class_record['subject_ids']) == 4985936 or int(class_record['subject_ids']) == 4989858:
        pass
    else:
        return False
    return True


with open(out_location, 'w', newline='') as file:
    fieldnames = ['classification_id',
                  'user_ip',
                  'workflow_id',
                  'workflow_version',
                  'created_at',
                  'gold_standard',
                  'subject_ids']
    writer = csv.DictWriter(file, fieldnames=fieldnames)
    writer.writeheader()

    i = 0
    j = 0
    with open(location) as f:
        r = csv.DictReader(f)
        for row in r:
            i += 1
            if include(row) is True:
                j += 1

                writer.writerow({'classification_id': row['classification_id'],
                                 'user_ip': row['user_ip'],
                                 'workflow_id': row['workflow_id'],
                                 'workflow_version': row['workflow_version'],
                                 'created_at': row['created_at'],
                                 'gold_standard': row['gold_standard'],
                                 'subject_ids': row['subject_ids']})

                print(j)
        print(i, 'lines read and inspected', j, 'records processed and copied')
        #
