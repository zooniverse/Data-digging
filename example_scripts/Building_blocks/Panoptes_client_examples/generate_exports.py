import os
import time
from datetime import datetime
from panoptes_client import Project, Panoptes

Panoptes.connect(username=os.environ['User_name'], password=os.environ['Password'])
project = Project.find(slug='pmason/fossiltrainer')


def generate_class(projt):
    try:
        meta_class = projt.describe_export('classifications')
        last_generated = meta_class['media'][0]['updated_at'][0:19]
        tdelta = (datetime.now() - datetime.strptime(last_generated, '%Y-%m-%dT%H:%M:%S')).total_seconds()
        if (300 + tdelta / 60) >= 24 * 60:  # 300 is offset EST offset from Zulu  could be 240 during EDT
            project.generate_export('classifications')
            print('Export request sent, please wait 30 seconds to verify generation has begun')
            time.sleep(30)
            meta_class = projt.describe_export('classifications')
            now_generated = meta_class['media'][0]['updated_at'][0:19]
            tdelta_now = (datetime.now() - datetime.strptime(now_generated, '%Y-%m-%dT%H:%M:%S')).total_seconds()
            if tdelta_now < 100:
                print(str(datetime.now())[0:19] + ' Classification export generated.')
                return True
            else:
                print(str(datetime.now())[0:19] + ' Classification export did not generate correctly')
                return False
        else:
            print(str(datetime.now())[0:19] + ' Too soon to generate Classification export - ' +
                  str(round((tdelta / 3600 + 5), 1)) + '  hrs.')
            return False
    except:
        print(str(datetime.now())[0:19] + ' Classification export did not generate correctly')
        return False


def generate_subj(projt):
    try:
        meta_subj = projt.describe_export('subjects')
        last_generated = meta_subj['media'][0]['updated_at'][0:19]
        tdelta = (datetime.now() - datetime.strptime(last_generated, '%Y-%m-%dT%H:%M:%S')).total_seconds()
        if (300 + tdelta / 60) >= 24 * 60:  # 300 is offset EST offset from Zulu  could be 240 during EDT
            project.generate_export('subjects')
            print('Export request sent, please wait 30 seconds to verify generation has begun')
            time.sleep(30)
            meta_subj = projt.describe_export('classifications')
            now_generated = meta_subj['media'][0]['updated_at'][0:19]
            tdelta_now = (datetime.now() - datetime.strptime(now_generated, '%Y-%m-%dT%H:%M:%S')).total_seconds()
            if tdelta_now < 100:
                print(str(datetime.now())[0:19] + ' Subject export generated.')
                return True
            else:
                print(str(datetime.now())[0:19] + ' Subject export did not generate correctly')
                return False
        else:
            print(str(datetime.now())[0:19] + ' Too soon to generate Subject export - ' +
                  str(round((tdelta / 3600 + 5), 1)) + '  hrs.')
            return False
    except:
        print(str(datetime.now())[0:19] + ' Subject export did not generate correctly')
        return False


if __name__ == '__main__':
    print(generate_class(project))
    print(generate_subj(project))
