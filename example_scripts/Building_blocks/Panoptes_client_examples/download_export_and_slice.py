import os
import csv
import requests
from datetime import datetime
from panoptes_client import Project, Panoptes

# this next line requires the Environmental Variables User_name and Password to be
# set to your zooniverse log in using your Operating system Controls.  Otherwise you
# can hardcode your username and password as in the line commented out, but then keep
# this code secure to protect your password!
Panoptes.connect(username=os.environ['User_name'], password=os.environ['Password'])
#  Panoptes.connect(username='User_name', password='Password')
#  Replace your project slug here:
project = Project.find(slug='pmason/fossiltrainer')
dstn_class = r'C:\py\SASClass\fossiltrainer-classifications.csv'
dstn_subj = r'C:\py\SASClass\fossiltrainer-subjects.csv'
out_location_class = r'C:\py\SASClass\snapshots-at-sea-classifications_short.csv'
out_location_subj = r'C:\py\SASClass\snapshots-at-sea-subjects_short.csv'


def download_file(url, dstn):
    request = requests.get(url, stream=True)
    with open(dstn, 'wb') as dstn_f:
        for chunk in request.iter_content(chunk_size=4096):
            dstn_f.write(chunk)
    return dstn


def download_exports(projt, dstn_cl, dstn_sb):
    # replace path and filename strings for where you want the exports saved in the next two lines:
    try:
        meta_class = projt.describe_export('classifications')
        generated = meta_class['media'][0]['updated_at'][0:19]
        tdelta = (datetime.now() - datetime.strptime(generated, '%Y-%m-%dT%H:%M:%S')).total_seconds()
        age = (300 + int(tdelta / 60))
        print(str(datetime.now())[0:19] + '  Classifications export', age, ' hours old')
        url_class = meta_class['media'][0]['src']
        file_class = download_file(url_class, dstn_cl)
        print(str(datetime.now())[0:19] + '  ' + file_class + ' downloaded')
    except:
        print(str(datetime.now())[0:19] + '  Classifications download did not complete')
        return False

    try:
        meta_subj = projt.describe_export('subjects')
        generated = meta_subj['media'][0]['updated_at'][0:19]
        tdelta = (datetime.now() - datetime.strptime(generated, '%Y-%m-%dT%H:%M:%S')).total_seconds()
        age = (300 + int(tdelta / 60))
        print(str(datetime.now())[0:19] + '  Subject export', age, ' hours old')
        url_subj = meta_subj['media'][0]['src']
        file_subj = download_file(url_subj, dstn_sb)
        print(str(datetime.now())[0:19] + '  ' + file_subj + ' downloaded')
    except:
        print(str(datetime.now())[0:19] + '  Subjects download did not complete')
        return False
    return True


def include_class(class_record):
    #  define a function that returns True or False based on whether the argument record is to be included or not in
    #  the output file based on the conditional clauses.
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
    if 100000000 >= int(class_record['subject_ids']) >= 0000:
        pass  # replace upper and lower subject_ids to include only a specified range of subjects - This is
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


def include_subj(subj_record):
    #  define a function that returns True or False based on whether the argument record is to be included or not in
    #  the output file based on the conditional clauses.
    #  many other conditions could be set up to determine if a record is to be processed and the flattened data
    #  written to the output file. Any or all of these conditional tests that are not needed can be deleted or
    # commented out with '#' placed in front of the line(s)of code that are not required.

    if int(subj_record['workflow_id']) != 0000:
        pass  # replace'!= 0000' with '== xxxx' where xxxx is any workflow linked to the project.
    else:
        return False
    if 100000 >= int(subj_record['subject_set_id']) >= 00000:
        pass  # replace '00000' and 100000 with first and last subject set to include.
    else:
        return False
    if 100000000 >= int(subj_record['subject_id']) >= 0000:
        pass  # replace upper and lower subject_ids to include only a specified range of subjects -this is
        # a very useful slice since subjects ids are sequentially assigned and increase with date and time created.  this is
    else:
        return False
    # otherwise :
    return True


def slice_exports(dstn_cl, out_location_cl, dstn_sb, out_location_sb):
    with open(out_location_cl, 'w', newline='') as file:
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

        # this area for initializing counters, status lists and loading pick lists into memory:
        i = 0
        j = 0

        #  open the zooniverse data file using dictreader
        with open(dstn_cl) as f:
            r = csv.DictReader(f)
            for row in r:
                i += 1
                if include_class(row):
                    j += 1
                    # This set up the writer to match the field names above and the variable names of their values:
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

    # This area prints some basic process info and status
    print(str(datetime.now())[0:19] + '  Classification file:' +
          ' ' + str(i) + ' lines read and inspected' + ' ' + str(j) + ' records selected and copied')

    k = 0
    m = 0
    with open(out_location_sb, 'w', newline='') as file:
        fieldnames = ['subject_id',
                      'project_id',
                      'workflow_id',
                      'subject_set_id',
                      'metadata',
                      'locations',
                      'classifications_count',
                      'retired_at',
                      'retirement_reason']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()

        #  open the zooniverse data file using dictreader
        with open(dstn_sb) as f:
            r = csv.DictReader(f)
            for row in r:
                k += 1
                if include_subj(row):
                    m += 1
                    # This set up the writer to match the field names above and the variable names of their values:
                    writer.writerow({'subject_id': row['subject_id'],
                                     'project_id': row['project_id'],
                                     'workflow_id': row['workflow_id'],
                                     'subject_set_id': row['subject_set_id'],
                                     'metadata': row['metadata'],
                                     'locations': row['locations'],
                                     'classifications_count': row['classifications_count'],
                                     'retired_at': row['retired_at'],
                                     'retirement_reason': row['retirement_reason']})

    print(str(datetime.now())[0:19] + '  Subjects file:' +
          ' ' + str(k) + ' lines read and inspected' + ' ' + str(m) + ' records selected and copied')
    return True


if __name__ == '__main__':
    print(download_exports(project, dstn_class, dstn_subj))
    print(slice_exports(dstn_class, out_location_class, dstn_subj, out_location_subj))
#
