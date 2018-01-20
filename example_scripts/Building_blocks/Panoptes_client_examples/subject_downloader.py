""" This version is written in Python 3.62,  it has been tested on Windows with only small
 subject sets, but appeared to work well.  Hopefully the OS related statements are suitably
 written to handle Mac path names."""
import os
import panoptes_client
from panoptes_client import SubjectSet, Panoptes
from PIL import Image
import requests

Panoptes.connect(username=os.environ['User_name'], password=os.environ['Password'])

while True:
    set_id = input('Enter subject set id to download:' + '\n')
    try:        
        print('Please wait while I check this subject set exists and how many subjects are in it')
        subject_set = SubjectSet.find(set_id)
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
              
saved_images =  0
for item in subject_list:
    try:
        file_name = location + os.sep + item.metadata['Filename']
    except KeyError:
        file_name = location + os.sep + item.id + '.' + (list(item.locations[0].keys())[0]).partition('/')[2].lower()
    
    if os.path.isfile(file_name):
        print(file_name, ' already exists, not downloaded')
        saved_images += 1
        continue

    # acquire the image
    try:
        acquired_image = Image.open(requests.get(list(item.locations[0].values())[0], stream=True).raw)
    except IOError:
        print('Subject download for ', item.id, ' failed')
        continue
   
    try:
        acquired_image.save(file_name, exif=acquired_image.info.get('exif'))
        saved_images += 1
        print(file_name)
    except TypeError:
        acquired_image.save(file_name)
        saved_images += 1
        print(file_name, ' no exif data recovered')
print(saved_images, ' files of ', len(subject_list), ' are in the directory at the end of downloading')
