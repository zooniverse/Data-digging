""" This version is written in Python 3.62,  it has been tested on Windows with only small
 subject sets, but appeared to work well.  Hopefully the OS related statements are suitably
 written to handle Mac path names."""
import os
import panoptes_client
from panoptes_client import SubjectSet, Panoptes
from PIL import Image
import requests

while True:
    User_name = input('Enter Zoonioverse User_name' + '\n')
    Password = input('Entre Zooniverse Password - Warning it will show on the screen' + '\n')
    try:
        Panoptes.connect(username=User_name, password=Password)
        break
    except panoptes_client.panoptes.PanoptesAPIException:
        print('Credentials not accepted')
        retry = input('Enter "n" to cancel, any other key to retry' + '\n')
        if retry.lower() == 'n':
            quit()

while True:
    set_id = input('Entry subject set id to download:' + '\n')
    try:
        # check if the subject set exits
        print('Please wait while I check this subject set exists and how many subjects are in it')
        subject_set = SubjectSet.where(subject_set_id=set_id).next()
        count_subjects = 0
        subject_list = []
        for subject in subject_set.subjects:
            count_subjects += 1
            subject_list.append(subject)
            print(subject)
        print('You have chosen to download ', len(subject_list), ' subjects from subject set ', set_id)
        retry = input('Enter "n" to cancel this download, any other key to continue' + '\n')
        if retry.lower() == 'n':
            quit()
        break
    except panoptes_client.panoptes.PanoptesAPIException:
        retry = input('Subject set not found, Enter "n" to cancel, any other key to retry' + '\n')
        if retry.lower() == 'n':
            quit()

while True:
    location = input('Enter the full path for the image directory to download to, or enter "." '
                     'to use the current directory' + '\n')
    if location == '.':
        location = os.getcwd()
        break
    else:
        if os.path.exists(location):
            break
        else:
            print('That entry is not a valid path for an existing directory')
            print('Example (Windows) "C:\Some_directory_name\Some_sub_directory"')
            print('Note, no closing slash')
            retry = input('Enter "n" to cancel, any other key to try again' + '\n')
            if retry.lower() == 'n':
                quit()
              
i =  0
for item in subject_list:
    try:
        file_name = location + os.sep + item.metadata['Filename']
    except KeyError:
        file_name = location + os.sep + item.id + '.jpg'
      
    print(file_name)
    if os.path.isfile(file_name):
        print(file_name, ' already exists, not downloaded')
        i += 1
        continue

    # acquire the image
    try:
        im = Image.open(requests.get(item.locations[0]['image/jpeg'], stream=True).raw)
    except IOError:
        print('Subject download for ', item.id, ' failed')
        continue
   
    try:
        im.save(file_name, exif=im.info.get('exif'))
        i += 1
    except TypeError:
        im.save(file_name)
        i += 1
        print('Subject ', item.id, ' no exif data recovered')
print(i, ' files of ', len(subject_list), ' are in the directory at the end of downloading')
