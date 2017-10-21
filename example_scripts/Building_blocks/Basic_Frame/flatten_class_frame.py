""" This script takes a local copy of the Zooniverse Classification download file as input and
provides a framework to which various code blocks are added to flatten the JSON format for the
annotations field into a more user friendly format. Which code blocks are required depends on
tasks in the specific project which generated the classification download.  This code also provides
an easy way to select specific records based on values of various fields in the standard classification
record.  The output file structure will be modified as blocks are added, splitting "annotations" out
into separate columns. Once certain fields in the original file are no longer needed (metadata,
subject_data and annotations) they can be removed to reduce the file size (usually by an order of
magnitude or more)."""

# this script was written in Python 3.6.2 "out of the box" and should run without any added packages.
import csv
import json
import sys
from datetime import datetime

csv.field_size_limit(sys.maxsize)

# Give full path and filenames for input and output files (these are user specific - this example was
# for the project Aerobotany.  The easiest way to get the full path and file name is to copy and paste
# from "Properties" (right click of file name in .
# Example: location = r'C:\py\AAClass\amazon-aerobotany-classifications_2017-03-18.csv'
location = r'modify this text to full path and file name including extension (.csv) for input file'
out_location = r'modify this text to full path and a file name including extension (.csv) for output file'


# define a function that returns True or False based on whether the argument record is to be included or not in
# the output file based on the conditional clauses.

def include(class_record):
    #  many other conditions could be set up to determine if a record is to be processed and the flattened data
    #  written to the output file. Any or all of these conditional tests that are not needed can be deleted or
    # commented out with '#' placed in front of the line(s)of code that are not required.

    if int(class_record['workflow_id']) != 0000:
        pass  # replace'!= 0000' with '== xxxx' where xxxx is the workflow to include.  This is also useful to
        # exclude a specific workflow as well.
    else:
        return False

    if float(class_record['workflow_version']) >= 001.01:
        pass  # replace '001.01' with first version of the workflow to include.
    else:
        return False

    if 10000000 >= int(class_record['subject_ids']) >= 1000:
        pass   # replace upper and lower subject_ids to include only a specified range of subjects - this is
        # a very useful slice since subjects are selected together and can still be aggregated.
    else:
        return False

    if not class_record['gold_standard'] and not class_record['expert']:
        pass  # this excludes gold standard and expert classifications - remove the "not" to select only
        # the gold standard or expert classifications
    else:
        return False

    if '2100-00-10 00:00:00 UTC' >= class_record['created_at'] >= '2000-00-10 00:00:00 UTC':
        pass   # replace earliest and latest created_at date and times to select records commenced in a
        #  specific time period
    else:
        return False

    # otherwise :
    return True


# prepare the output file and write the header
with open(out_location, 'w', newline='') as file:
    # The list of field names must include each field required in the output. The names, and order must be exactly
    # the same here as in the writer statement near the end of the program. The names and order are arbitary -
    # your choice, as long as they are the same in both locations.
    # As code blocks are added to flatten the annotations JSON, columns need to be added to contain each newly
    # split out group of data. Add each one using the format "' new_field_name'," .  Similarly fields can be removed
    # from both places to reduce the file size if the iformation is not needed for the current purpose.
    fieldnames = ['classification_id',
                  'user_name', 'user_id',
                  'user_ip', 'workflow_id',
                  'workflow_name',
                  'workflow_version',
                  'created_at',
                  'gold_standard',
                  'expert',
                  'metadata',
                  'annotations',
                  'subject_data',
                  'subject_ids']
    writer = csv.DictWriter(file, fieldnames=fieldnames)
    writer.writeheader()

    i = 0
    j = 0
    #  open the zooniverse data file using dictreader,  and loads the more complex json strings as python objects
    with open(location) as f:
        r = csv.DictReader(f)
        for row in r:
            i += 1
            # useful for debugging - set the number of record to process at a low number ~1000
            if i == 150000:  # one more than the last line of zooniverse file read if not EOF
                break
            if include(row) is True:
                j += 1
                # once we begin working with these JSON format columns we will need to load the json
                #  strings as python objects (dictionaries and lists) by removing the '#' from these three lines:
                # annotations = json.loads(row['annotations'])
                # subject_data = json.loads(row['subject_data'])
                # metadata = json.loads(row['metadata'])

                # this is the area the various blocks of code will be inserted to perform the required operations
                # to flatten the annotations field, preform additional general tasks, or test the data for various
                # conditions.

                writer.writerow({'classification_id': row['classification_id'],
                                 'user_name': row['user_name'],
                                 'user_id': row['user_id'],
                                 'user_ip': row['user_ip'],
                                 'workflow_id': row['workflow_id'],
                                 'workflow_name': row['workflow_name'],
                                 'workflow_version': row['workflow_version'],
                                 'created_at': row['created_at'],
                                 'gold_standard': row['gold_standard'],
                                 'expert': row['expert'],
                                 'metadata': row['metadata'],
                                 'annotations': row['annotations'],
                                 'subject_data': row['subject_data'],
                                 'subject_ids': row['subject_ids']})

                print(j)  # just so we know progress is being made

        print(i, 'lines read and inspected', j, 'records processed and copied')
        #
