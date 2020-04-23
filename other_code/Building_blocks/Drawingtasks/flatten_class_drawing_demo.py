""" This script has been built up using the basic frame and various general utility and question blocks plus
the drawing1 block for circles, without details.  It fully flattens Aerobotany classifications into a form suitable
for aggregating over all users by subject_ids."""

# this script was written in Python 3.6.2 "out of the box" and should run without any added packages.
import csv
import json
import sys
from datetime import datetime

csv.field_size_limit(sys.maxsize)

# File location section:

location = r'C:\py\AAClass\amazon-aerobotany-classifications_2017-03-18.csv'
out_location = r'C:\py\Data_digging\flatten_class_drawing_demo.csv'
name_location = r'C:\py\AAusers\AAipusers.csv'


# Function definitions needed for any blocks.


def include(class_record):
    if int(class_record['workflow_id']) == 3130:
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


def load_pick_ip():
    with open(name_location) as name:
        ipdict = csv.DictReader(name)
        assigned_name = {}
        for ipline in ipdict:
            assigned_name[str(ipline['user_ip'])] = ipline['assigned_name']
        return assigned_name


def pull_circle(drawn_object, task_label):
    x = int(round((drawn_object['x']), 0))
    y = int(round((drawn_object['y']), 0))
    r = int(round((drawn_object['r']), 0))
    #  various functions to test the validity of the drawing can be added
    #  here. See flatten_class_tests.py if available
    #  detail = [item['value'] for item in drawn_object['details']]
    #  dropped detail from the drawing list for this demo
    drawing = [x, y, r, task_label]   # , detail]
    return drawing


# Set up the output file structure with desired fields:
# prepare the output file and write the header
with open(out_location, 'w', newline='') as file:
    fieldnames = ['line_number',
                  'subject_ids',
                  'image_number',
                  'user_name',
                  'workflow_id',
                  'workflow_version',
                  'classification_id',
                  'created_at',
                  'elasped_time',
                  'image_size',
                  'first_task',
                  'H palm',
                  'flowering',
                  'leafless'
                  ]
    writer = csv.DictWriter(file, fieldnames=fieldnames)
    writer.writeheader()

    # this area for initializing counters, status lists and loading pick lists into memory:
    i = 0
    j = 0
    name_list = load_pick_ip()
    no_size = []
    labels = {0: "h", 1: "f", 2: "l"}

    #  open the zooniverse data file using dictreader,  and load the more complex json strings as python objects
    with open(location) as f:
        classifications = csv.DictReader(f)
        for row in classifications:
            i += 1
            if i == 12000:  # demo - only read part of file
                break
            if include(row) is True:
                j += 1
                subject_data = json.loads(row['subject_data'])
                metadata = json.loads(row['metadata'])
                annotations = json.loads(row['annotations'])

                # generate user_name for not_signed_in users
                user_name = str(row['user_name'])
                if row['user_id'] == '':
                    try:
                        user_name = name_list[str(row['user_ip'])]
                    except KeyError:
                        user_name = 'Visitor'  # this lumps them all together

                # generate image_number from the subject data field Example 1
                #  Subject_data contains text similar to this:
                # '{"3350842":{"retired":null,"Filename":"RUTA470M_Sector4_190816094.jpg"}}'
                line = str(row['subject_data'])
                start = line.find('Filename')
                end = line.find('.jpg')
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
                    image_size = [round(widths['naturalWidth']), round(widths['naturalHeight'])]
                else:
                    no_size.append(row['subject_ids'])
                    image_size = [2000, 1500]

                # generate First task
                first_task = annotations[0]
                task_answer = str(first_task['value'])

                # pull out [x, y, r], rounds data Uses Block 1 of flatten_class_drawing.py.
                drawings_0 = []
                drawings_1 = []
                drawings_2 = []
                for task in annotations:
                    try:
                        if 'Circle crowns' in task['task_label']:
                            for drawing_object in task['value']:
                                if drawing_object['x'] is not None:
                                    if drawing_object['tool'] is 0:
                                        drawings_0.append(pull_circle(drawing_object, labels[0]))
                                    if drawing_object['tool'] is 1:
                                        drawings_1.append(pull_circle(drawing_object, labels[1]))
                                    if drawing_object['tool'] is 2:
                                        drawings_2.append(pull_circle(drawing_object, labels[2]))
                    except KeyError:
                        continue
                # return lists to JSON string format prior to writing them to file
                drawings_0 = json.dumps(drawings_0)
                drawings_1 = json.dumps(drawings_1)
                drawings_2 = json.dumps(drawings_2)

                # This set up the writer to match the field names above and the variable names of their values:
                writer.writerow({'line_number': str(i),
                                 'subject_ids': row['subject_ids'],
                                 'image_number': image_number,
                                 'user_name': user_name,
                                 'workflow_id': row['workflow_id'],
                                 'workflow_version': row['workflow_version'],
                                 'classification_id': row['classification_id'],
                                 'created_at': row['created_at'],
                                 'elasped_time': tdelta,
                                 'image_size': image_size,
                                 'first_task': task_answer,
                                 'H palm': drawings_0,
                                 'flowering': drawings_1,
                                 'leafless': drawings_2
                                 })
                print(j)  # just so we know progress is being made
        # This area prints some basic process info and status
        print(i, 'lines read and inspected', j, 'records processed and copied')
        print('classifications with no image size', no_size)
        #
