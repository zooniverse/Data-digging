""" This script is flatten_classification_frame.py with several blocks added from
flatten_classification_general_utilities.py  which 1)add an assigned_name for higher volume not-logged-in users
from an externally generated list, 2) added a image_number generated from the file name in the subject_data
field of the original classification file, 3) added an elapsed_time calculated from the started and finished
times in the metadata field of the original classification, and 4) added image_size based on the natural
dimensions in the metadata field. As few other modifications as possible were made, carefully following the
instructions in the comments in flatten_classification_general_utilities.py.  """

# this script was written in Python 3.6.2 "out of the box" and should run without any added packages.
import csv
import json
import sys
from datetime import datetime

csv.field_size_limit(sys.maxsize)

# File location section:
# Give full path and file names for input and output files (these are user specific - this example was
# for the project Aerobotany.  The easiest way to get the full path and file name is to copy and paste
# from "Properties" (right click of file name in.
location = r'C:\py\AAClass\amazon-aerobotany-classifications_2017-03-18.csv'
out_location = r'C:\py\Data_digging\flatten_classification_general_utilities_demo_2.csv'
name_location = r'C:\py\AAusers\AAipusers.csv'


# Function definitions needed for any blocks.
#  define a function that returns True or False based on whether the argument record is to be included or not in
# the output file based on the conditional clauses.

def include(class_record):
    #  many other conditions could be set up to determine if a record is to be processed and the flattened data
    #  written to the output file. Any or all of these conditional tests that are not needed can be deleted or
    # commented out with '#' placed in front of the line(s)of code that are not required.

    if int(class_record['workflow_id']) == 3130:
        pass  # replace'!= 0000' with '== xxxx' where xxxx is the workflow to include.  This is also useful to
        # exclude a specific workflow as well.
    else:
        return False
    if float(class_record['workflow_version']) >= 001.01::
        pass  # replace '001.01' with first version of the workflow to include.
    else:
        return False
    if 10000000 >= int(class_record['subject_ids']) >= 1000:
        pass  # replace upper and lower subject_ids to include only a specified range of subjects - this is
        # a very useful slice since subjects are selected together and can still be aggregated.
    else:
        return False
    if not class_record['gold_standard'] and not class_record['expert']:
        pass  # this excludes gold standard and expert classifications - remove the "not" to select only
        # the gold standard or expert classifications
    else:
        return False
    if '2100-00-10 00:00:00 UTC' >= class_record['created_at'] >= '2000-00-10 00:00:00 UTC':
        pass  # replace earliest and latest created_at date and times to select records commenced in a
        #  specific time period
    else:
        return False
    # otherwise :
    return True


def load_pick_ip():
    with open(name_location) as name:
        ipdict = csv.DictReader(name)
        assigned_name = {}
        for ipline in ipdict:
            assigned_name[str(ipline['user_ip'])] = ipline['assigned_name']
        return assigned_name


# Set up the output file structure with desired fields:
# prepare the output file and write the header
with open(out_location, 'w', newline='') as file:
    # The list of field names must include each field required in the output. The names, and order must be exactly
    # the same here as in the writer statement near the end of the program. The names and order are arbitary -
    # your choice, as long as they are the same in both locations.
    # As code blocks are added to flatten the annotations JSON, columns need to be added to contain each newly
    # split out group of data. Add each one using the format "' new_field_name'," .  Similarly fields can be removed
    # from both places to reduce the file size if the iformation is not needed for the current purpose.
    fieldnames = ['line_number',
                  'classification_id',
                  'user_name',
                  'workflow_id',
                  'workflow_version',
                  'created_at',
                  'elasped_time',
                  'image_size',
                  'subject_ids',
                  'image_number']
    writer = csv.DictWriter(file, fieldnames=fieldnames)
    writer.writeheader()

    # this area for initializing counters, status lists and loading pick lists into memory:
    i = 0
    j = 0
    name_list = load_pick_ip()
    no_size = []

    # In this area place lines that initialize variables or load dictionaries needed by the additional code blocks
    # that will be added to this frame.

    #  open the zooniverse data file using dictreader,  and load the more complex json strings as python objects
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
                subject_data = json.loads(row['subject_data'])
                metadata = json.loads(row['metadata'])

                # generate user_name for not_signed_in users
                user_name = str(row['user_name'])
                if row['user_id'] == '':
                    try:
                        user_name = name_list[str(row['user_ip'])]
                    except KeyError:
                        #  Various options for the case no user_name was assigned to that user_ip  - pick one!
                        user_name = 'Visitor'  # this lumps them all together

                # generate image_number from the subject data field Example 1
                #  Subject_data contains text similar to this:
                # '{"3350842":{"retired":null,"Filename":"RUTA470M_Sector4_190816094.jpg"}}'
                line = str(row['subject_data'])
                start = line.find('Filename')
                end = line.find('.jpg')
                # having found the start and end of the filename text, adjust the offsets to slice the string
                # exactly where you want (note start = the first character  of the search string, and end does
                # not include the search string.
                image_number = line[start + 11:end]

                # generate the classification elapsed_time, which is more useful than start/finish times
                #  "started_at":"2015-08-21T07:34:22.193Z",....,"finished_at":"2015-08-21T07:34:31.928Z"...
                line = str(row['metadata'])
                start = line.find("started")
                end = line.find('Z', start)
                begin = line[start + 13:end - 4]
                start = line.find('finished')
                end = line.find('Z', start)
                finish = line[start + 14:end - 4]
                tdelta = datetime.strptime(finish, '%Y-%m-%dT%H:%M:%S') - datetime.strptime(begin, '%Y-%m-%dT%H:%M:%S')
                if len(str(tdelta)) > 8:
                    tdelta = '24:00:00'

                # generate scale from metadata
                dimensions = metadata['subject_dimensions']
                widths = dimensions[0]
                if widths is not None:
                    image_size = json.dumps([round(widths['naturalWidth']),
                                             round(widths['naturalHeight'])])
                else:
                    no_size.append(row['classification_id'])
                    image_size = json.dumps([2000, 1500])

                # This set up the writer to match the field names above and the variable names of their values:
                writer.writerow({'line_number': str(i),
                                 'classification_id': row['classification_id'],
                                 'user_name': user_name,
                                 'workflow_id': row['workflow_id'],
                                 'workflow_version': row['workflow_version'],
                                 'created_at': row['created_at'],
                                 'elasped_time': tdelta,
                                 'image_size': image_size,
                                 'subject_ids': row['subject_ids'],
                                 'image_number': image_number})
                print(j)  # just so we know progress is being made
        # This area prints some basic process info and status
        print(i, 'lines read and inspected', j, 'records processed and copied')
        print('classifications with no image size', no_size)
        #
