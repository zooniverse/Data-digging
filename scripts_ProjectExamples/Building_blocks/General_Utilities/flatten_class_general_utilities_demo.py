import csv
import json
import sys
from datetime import datetime

csv.field_size_limit(sys.maxsize)
# file location area:
location = r'C:\py\FFClass\fossil-finder-classifications_test.csv'
out_location = r'C:\py\Data_digging\flatten_classification_general_utilities_demo.csv'
name_location = r'C:\py\FFIPusers\fossil-finder-classifications_IPusers.csv'
image_location = r'C:\py\FFSubject\fossil-finder-classifications_image_number.csv'

# define functions area:


def include(class_record):
    if int(class_record['workflow_id']) != 1961:
        pass
    else:
        return False
    if 3999999 >= int(class_record['subject_ids']) >= 3270000:
        pass
    else:
        return False
    if not class_record['gold_standard'] and not class_record['expert']:
        pass
    else:
        return False
    return True


def load_pick_ip():
    with open(name_location) as name:
        ipdict = csv.DictReader(name)
        assigned_name = {}
        for ipline in ipdict:
            assigned_name[str(ipline['user_ip'])] = ipline['assigned_name']
        return assigned_name


def load_pick_image():
    with open(image_location) as image:
        subject_dict = csv.DictReader(image)
        assigned_number = {}
        for subject_line in subject_dict:
            assigned_number[str(subject_line['subject_ids'])] = subject_line['image_number']
        return assigned_number


with open(out_location, 'w', newline='') as file:
    # Note we have added a number of fields including 'line_number and changed the order to suit our whims -
    # The write statement must match both items and order
    fieldnames = ['line_number',
                  'subject_ids',
                  'image_number',
                  'user_name',
                  'workflow_id',
                  'workflow_version',
                  'classification_id',
                  'created_at',
                  'elapsed_time',
                  'image_size']
    writer = csv.DictWriter(file, fieldnames=fieldnames)
    writer.writeheader()

# Initialize and load pick lists
    i = 0
    j = 0
    name_list = load_pick_ip()
    image_list = load_pick_image()
    no_image = []
    no_size = []

    with open(location) as f:
        r = csv.DictReader(f)
        for row in r:
            i += 1
            if i == 680000:
                break
            if include(row) is True:
                j += 1
                metadata = json.loads(row['metadata'])

                # Area to add the blocks that work on each record of the classification

                # generate user_name for not_signed_in users
                user_name = str(row['user_name'])
                if row['user_id'] == '':
                    try:
                        user_name = name_list[str(row['user_ip'])]
                    except KeyError:
                        user_name = 'Visitor'
                        #  user_name = str(row[user_name])
                        #  user_name = row['user_ip']

                # Use a subject_ids-image_name cross-reference to add image_numbers
                try:
                    image_number = image_list[str(row['subject_ids'])]
                except KeyError:
                    image_number = 'No_image'
                    no_image.append(row['subject_ids'])

                # generate the classification duration, which is more useful than start/finish times
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
                    image_size = json.dumps([795, 545])

                # Writer must agree with open field names and assign correct values to the fields
                writer.writerow({'line_number': str(i),
                                 'subject_ids': row['subject_ids'],
                                 'image_number': image_number,
                                 'user_name': user_name,
                                 'workflow_id': row['workflow_id'],
                                 'workflow_version': row['workflow_version'],
                                 'classification_id': row['classification_id'],
                                 'created_at': row['created_at'],
                                 'elapsed_time': str(tdelta),
                                 'image_size': image_size})
            print(i, j)
        # Area to print final status report
        print(i, 'lines read and inspected', j, 'records processed and copied')
        print('subjects with no image number', no_image)
        print('classifications with no image size', no_size)

        #
