""" This demo takes a classification where up to five dates have been marked using one tool and transcribed
two ways in a two step sub-task - first a verbatim transcription, then as a specific date format. Each tool
usage is sorted by its location from the top of the page down and each location and the two dates are
given their columns in the output.  Then a simple transcription of one specific line is pulled out and given
its own column as well. This results in a csv file where each transcription is in a designated column.  It is
in a format that can be directly reconciled with Notes from Natures reconcile.py appropriately set up with the
csv file parameter and the column names we want to reconcile.
As usual it starts with flatten_class_frame.py, drops unneeded sections, and adds in the necessary blocks
from flatten_class_transcription.py with slight modifications specific to the project task labels.  As well
there is a modification to split out the dual sub-task into transcription_0 and transcription_1 as shown below."""

# this script was written in Python 3.6.2 "out of the box" and should run without any added packages.
import csv
import json
import sys

csv.field_size_limit(sys.maxsize)

location = r'C:\py\Data_digging\example_classifications.csv'
out_location = r'C:\py\Data_digging\flatten_class_transcription_demo.csv'

# Function definitions needed for any blocks.


def include(class_record):
    # select one workflow only:
    if int(class_record['workflow_id']) == 4870:
        pass
    else:
        return False
    return True


# Set up the output file structure with desired fields:
# prepare the output file and write the header
with open(out_location, 'w', newline='') as file:

    fieldnames = ['classification_id',
                  'user_name', 'user_id',
                  'workflow_id',
                  'location_1',
                  'transcribed_1',
                  'formatted_1',
                  'location_2',
                  'transcribed_2',
                  'formatted_2',
                  'location_3',
                  'transcribed_3',
                  'formatted_3',
                  'location_4',
                  'transcribed_4',
                  'formatted_4',
                  'location_5',
                  'transcribed_5',
                  'formatted_5',
                  'first line',
                  'subject_id']  # note for reasons unknown, when working with csv files, Notes from
    # Nature's reconciliation script reconcile.py requires the column holding the subject numbers to be
    # called subject_id with no 's' while the classification download uses subject_ids (with an 's').

    writer = csv.DictWriter(file, fieldnames=fieldnames)
    writer.writeheader()

    # this area for initializing counters, status lists and loading pick lists into memory:
    i = 0
    j = 0
    n = 5  # this is the maximum number of tool uses this script can handle

    #  open the zooniverse data file using dictreader,  Load the more complex json strings as python objects
    with open(location) as f:
        r = csv.DictReader(f)
        for row in r:
            i += 1
            if include(row) is True:
                j += 1
                annotations = json.loads(row['annotations'])

                # this is the area the various blocks of code are inserted
                # reset the drawings and transcription variables for each record
                drawings = [[] for d in range(0, n)]
                transcription_0 = ['' for t in range(0, n)]
                transcription_1 = ['' for t in range(0, n)]
                first_line = []

                for task in annotations:

                    try:
                        if 'Place green rectangles' in task['task_label']:
                            #  use a decorate-sort-undecorate to order the drawings from the top of the page to
                            #  the bottom no matter what order they were drawn in.
                            decorate = [(item['y'], item) for item in task['value']]
                            decorate.sort()
                            undecorate = [item[1] for item in decorate]

                            for drawing in range(0, n):  # loop over n drawings
                                try:
                                    if undecorate[drawing] is not None:
                                        drawing_object = undecorate[drawing]
                                        # round to desired accuracy in pixels (0 or 1 decimal is about optimum)
                                        x = round(drawing_object['x'], 0)
                                        y = round(drawing_object['y'], 0)
                                        w = round(drawing_object['width'], 0)
                                        h = round(drawing_object['height'], 0)
                                        drawings[drawing] = json.dumps([x, y, w, h])
                                        try:
                                            transcription_0[drawing] = drawing_object['details'][0]['value']
                                        except IndexError:
                                            transcription_0[drawing] = ''
                                        try:
                                            transcription_1[drawing] = drawing_object['details'][1]['value']
                                        except IndexError:
                                            transcription_1[drawing] = ''

                                except IndexError:
                                    drawings[drawing] = []
                                    transcription_0[drawing] = ''
                                    transcription_1[drawing] = ''
                                continue
                    except KeyError:
                        continue

                    # add block for simple transcription of one field:
                    try:
                        if 'Transcribe first line' in task['task_label']:
                            if task['value'] is not None:
                                first_line = str(task['value'])
                    except KeyError:
                        continue

                # This set up the writer to match the field names above and the variable names of their values:
                writer.writerow({'classification_id': row['classification_id'],
                                 'user_name': row['user_name'],
                                 'user_id': row['user_id'],
                                 'workflow_id': row['workflow_id'],
                                 'location_1': drawings[0],
                                 'transcribed_1': transcription_0[0],
                                 'formatted_1': transcription_1[0],
                                 'location_2': drawings[1],
                                 'transcribed_2': transcription_0[1],
                                 'formatted_2': transcription_1[1],
                                 'location_3': drawings[2],
                                 'transcribed_3': transcription_0[2],
                                 'formatted_3': transcription_1[2],
                                 'location_4': drawings[3],
                                 'transcribed_4': transcription_0[3],
                                 'formatted_4': transcription_1[3],
                                 'location_5': drawings[4],
                                 'transcribed_5': transcription_0[4],
                                 'formatted_5': transcription_1[4],
                                 'first line': first_line,
                                 'subject_id': row['subject_ids']})

                print(j)  # just so we know progress is being made
        # This area prints some basic process info and status
        print(i, 'lines read and inspected', j, 'records processed and copied')
        #
