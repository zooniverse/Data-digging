""" This script has been built up using the basic frame plus the drawing blocks for various tool types."""

# this script was written in Python 3.6.2 "out of the box" and should run without any added packages.
import csv
import json
import sys

csv.field_size_limit(sys.maxsize)

# File location section:
# Give full path and file names for input and output files (these are user specific - this example was
# for the project Aerobotany.  The easiest way to get the full path and file name is to copy and paste
# from "Properties" (right click of file name in.
location = r'C:\py\Data_digging\example_classifications.csv'
out_location = r'C:\py\Data_digging\flatten_class_drawing_demo2.csv'

# Function definitions needed for any blocks.


def include(class_record):
    if int(class_record['workflow_id']) == 4759:
        pass  # replace'!= 0000' with '== xxxx' where xxxx is the workflow to include.  This is also useful to
        # exclude a specific workflow as well.
    else:
        return False
    if not class_record['gold_standard'] and not class_record['expert']:
        pass  # this excludes gold standard and expert classifications - remove the "not" to select only
        # the gold standard or expert classifications
    else:
        return False
    # otherwise :
    return True


def pull_point(drawn_object, task_label):
    x = round(drawn_object['x'], 0)
    y = round(drawn_object['y'], 0)
    #  various functions to test the validity of the drawing can be added
    #  here. See flatten_class_tests.py if available
    detail = [item['value'] for item in drawn_object['details']]
    drawing = [x, y, task_label, detail]
    return drawing


def pull_circle(drawn_object, task_label):
    x = round(drawn_object['x'], 0)
    y = round(drawn_object['y'], 0)
    r = round(drawn_object['r'], 0)
    #  various functions to test the validity of the drawing can be added
    #  here. See flatten_class_tests.py if available
    detail = [item['value'] for item in drawn_object['details']]
    drawing = [x, y, r, task_label, detail]
    return drawing


def pull_line(drawn_object, task_label):
    x1 = round(drawn_object['x1'], 0)
    y1 = round(drawn_object['y1'], 0)
    x2 = round(drawn_object['x2'], 0)
    y2 = round(drawn_object['y2'], 0)
    #  various functions to test the validity of the drawing can be added
    #  here. See flatten_class_tests.py if available
    detail = [item['value'] for item in drawn_object['details']]
    drawing = [x1, y1, x2, y2, task_label, detail]
    return drawing


def pull_rectangle(drawn_object, task_label):
    x = round(drawn_object['x'], 0)
    y = round(drawn_object['y'], 0)
    w = round(drawn_object['width'], 0)
    h = round(drawn_object['height'], 0)
    #  various functions to test the validity of the drawing can be added
    #  here. See flatten_class_tests.py if available
    detail = [item['value'] for item in drawn_object['details']]
    drawing = [x, y, w, h, task_label, detail]
    return drawing


def pull_column(drawn_object, task_label):
    x = round(drawn_object['x'], 0)
    w = round(drawn_object['width'], 0)
    #  various functions to test the validity of the drawing can be added
    #  here. See flatten_class_tests.py if available
    detail = [item['value'] for item in drawn_object['details']]
    drawing = [x, w, task_label, detail]
    return drawing


def pull_triangle(drawn_object, task_label):
    r = round(drawn_object['r'], 0)
    x = round(drawn_object['x'], 0)
    y = round(drawn_object['y'], 0)
    a = round(drawn_object['angle'], 2)
    #  various functions to test the validity of the drawing can be added
    #  here. See flatten_class_tests.py if available
    detail = [item['value'] for item in drawn_object['details']]
    drawing = [r, x, y, a, task_label, detail]
    return drawing


def pull_ellipse(drawn_object, task_label):
    x = round(drawn_object['x'], 0)
    y = round(drawn_object['y'], 0)
    rx = round(drawn_object['rx'], 0)
    ry = round(drawn_object['ry'], 0)
    a = round(drawn_object['angle'], 2)
    #  various functions to test the validity of the drawing can be added
    #  here. See flatten_class_tests.py if available
    detail = [item['value'] for item in drawn_object['details']]
    drawing = [x, y, rx, ry, a, task_label, detail]
    return drawing


# Set up the output file structure with desired fields:
# prepare the output file and write the header
with open(out_location, 'w', newline='') as file:
    fieldnames = ['line_number',
                  'subject_ids',
                  'workflow_id',
                  'workflow_version',
                  'classification_id',
                  'created_at',
                  'line_one',
                  'line_two',
                  'rectangle_one',
                  'triangle_one',
                  'ellipse_one',
                  'column_one'
                  ]
    writer = csv.DictWriter(file, fieldnames=fieldnames)
    writer.writeheader()

    # this area for initializing counters, status lists and loading pick lists into memory:
    i = 0
    j = 0
    labels = {0: "L1", 1: "L2", 2: "R", 3: "E", 4: "T", 5: "Col"}

    #  open the zooniverse data file using dictreader,  and load the more complex json strings as python objects
    with open(location) as f:
        classifications = csv.DictReader(f)
        for row in classifications:
            i += 1
            # useful for debugging - set the number of record to process at a low number ~1000
            if i == 12000:  # one more than the last line of zooniverse file read if not EOF
                break
            if include(row) is True:
                j += 1
                # once we begin working with these JSON format columns we will need to load the json
                #  strings as python objects (dictionaries and lists) by removing the '#' from these three lines:
                subject_data = json.loads(row['subject_data'])
                metadata = json.loads(row['metadata'])
                annotations = json.loads(row['annotations'])

                # Flatten drawing tasks
                # reset the drawing lists
                drawings_1_0 = []
                drawings_1_1 = []
                drawings_1_2 = []
                drawings_1_3 = []
                drawings_1_4 = []
                drawings_1_5 = []

                for task in annotations:
                    try:
                        if 'Line drawing' in task['task_label']:
                            for drawing_object in task['value']:
                                if drawing_object['tool'] is 0:
                                    drawings_1_0.append(pull_line(drawing_object, labels[0]))
                                if drawing_object['tool'] is 1:
                                    drawings_1_1.append(pull_line(drawing_object, labels[1]))
                                if drawing_object['tool'] is 2:
                                    drawings_1_2.append(pull_rectangle(drawing_object, labels[2]))
                                if drawing_object['tool'] is 3:
                                    drawings_1_3.append(pull_ellipse(drawing_object, labels[3]))
                                if drawing_object['tool'] is 4:
                                    drawings_1_4.append(pull_triangle(drawing_object, labels[4]))
                                if drawing_object['tool'] is 5:
                                    drawings_1_5.append(pull_column(drawing_object, labels[5]))
                    except KeyError:
                        continue
                drawings_1_0 = json.dumps(drawings_1_0)
                drawings_1_1 = json.dumps(drawings_1_1)
                drawings_1_2 = json.dumps(drawings_1_2)
                drawings_1_3 = json.dumps(drawings_1_3)
                drawings_1_4 = json.dumps(drawings_1_4)
                drawings_1_5 = json.dumps(drawings_1_5)

                # This sets up the writer to match the field names above and the variable names of their values:
                writer.writerow({'line_number': str(i),
                                 'subject_ids': row['subject_ids'],
                                 'workflow_id': row['workflow_id'],
                                 'workflow_version': row['workflow_version'],
                                 'classification_id': row['classification_id'],
                                 'created_at': row['created_at'],
                                 'line_one': drawings_1_0,
                                 'line_two': drawings_1_1,
                                 'rectangle_one': drawings_1_2,
                                 'triangle_one': drawings_1_4,
                                 'ellipse_one': drawings_1_3,
                                 'column_one': drawings_1_5
                                 })
                print(j)  # just so we know progress is being made
        # This area prints some basic process info and status
        print(i, 'lines read and inspected', j, 'records processed and copied')
#
