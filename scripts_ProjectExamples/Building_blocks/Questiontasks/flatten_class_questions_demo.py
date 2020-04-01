import csv
import json
import sys

csv.field_size_limit(sys.maxsize)
# file location area:
location = r'C:\py\FFClass\fossil-finder-classifications_test.csv'
out_location = r'C:\py\Data_digging\flatten_class_questions_demo.csv'
name_location = r'C:\py\FFIPusers\IPuser.csv'


# define functions area:


def include(class_record):
    if int(class_record['workflow_id']) == 371:
        pass
    else:
        return False
    if float(class_record['workflow_version']) >= 160.01:
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


with open(out_location, 'w', newline='') as file:
    # Note we have added a number of fields including 'line_number and changed the order to suit our whims -
    # The write statement must match both items and order
    fieldnames = ['line_number',
                  'subject_ids',
                  'user_name',
                  'workflow_id',
                  'workflow_version',
                  'classification_id',
                  'created_at',
                  'image_quality',
                  'ground_coverage',
                  'surface_material']

    writer = csv.DictWriter(file, fieldnames=fieldnames)
    writer.writeheader()

    # Initialize and load pick lists
    i = 0
    j = 0
    name_list = load_pick_ip()
    task_answer_template_1 = ['OK to', 'Blurry', 'Noisy', 'Bushy', 'Dark']
    with open(location) as f:
        r = csv.DictReader(f)
        for row in r:
            i += 1
            if i == 3000:
                break
            if include(row) is True:
                j += 1
                metadata = json.loads(row['metadata'])
                annotations = json.loads(row['annotations'])

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

                task_vector_1 = [0, 0, 0, 0, 0]
                task_answer_2 = ''
                task_answer_3 = ''

                for task in annotations:
                    # Even though the first question only allows single answers we will use Block 4 - Multiple-
                    # allowed answer question - answer vector method to record it:
                    try:
                        if 'good enough' in task['task_label']:
                            for k in range(0, 5):
                                if task_answer_template_1[k] in task['value']:
                                    task_vector_1[k] = 1
                            if task_vector_1 == [0, 0, 0, 0, 0]:  # no answers selected
                                task_vector_1 = []
                    except (TypeError, KeyError):
                        task_vector_1 = ''
                        continue
                    # The second question is a single required answer with short answers that need no massaging
                    try:
                        if 'ground cover' in task['task_label']:
                            if task['value'] is not None:
                                task_answer_2 = str(task['value'])
                    except KeyError:
                        continue
                    # The third question is also a simple single answer. These are short answers except for one
                    # we will shorten:
                    try:
                        if 'made of' in task['task_label']:
                            if task['value'] is not None:
                                task_answer_3 = str(task['value'])
                                if task_answer_3.find('Silt') >= 0:
                                    task_answer_3 = 'Mud'
                    except KeyError:
                        continue
                task_vector_1 = json.dumps(task_vector_1)

                # Writer must agree with open field names and assign correct values to the fields
                writer.writerow({'line_number': str(i),
                                 'subject_ids': row['subject_ids'],
                                 'user_name': user_name,
                                 'workflow_id': row['workflow_id'],
                                 'workflow_version': row['workflow_version'],
                                 'classification_id': row['classification_id'],
                                 'created_at': row['created_at'],
                                 'image_quality': task_vector_1,
                                 'ground_coverage': task_answer_2,
                                 'surface_material': task_answer_3})
            print(i, j)
        # Area to print final status report
        print(i, 'lines read and inspected', j, 'records processed and copied')

        #
