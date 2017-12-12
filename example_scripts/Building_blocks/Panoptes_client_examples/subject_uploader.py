""" This version is written in Python 3.62,  it has been tested on Windows with only small
 subject sets, but appeared to work well.  Hopefully the OS related statements are suitably
 written to handle Mac path names."""
import os
import panoptes_client
from panoptes_client import SubjectSet, Subject, Project, Panoptes

Panoptes.connect(username=os.environ['User_name'], password=os.environ['Password'])
project = Project.find(slug='pmason/fossiltrainer')

while True:
    location = input('Enter the full path for the image directory, or enter "." '
                     'to use the current directory' + '\n')
    if location == '.':
        location = os.getcwd()
        break
    else:
        if os.path.exists(location):
            break
        else:
            print('That entry is not a valid path for an existing directory')
            retry = input('Enter "y" to try again, any other key to exit' + '\n')
            if retry.lower() != 'y':
                quit()

# load the list of image files found in the directory:
# The local Filename is the only metadata included here - if additional metadata is
# required the dictionary subject_metadata can be expanded here with additional code
# to pull the metadata from another source, or it can be updated later with an additional script.
file_types = ['jpg', 'jpeg', 'png', 'gif', 'svg']
subject_metadata = {}
for entry in os.listdir(location):
    if entry.partition('.')[2].lower() in file_types:
        subject_metadata[entry] = {'Filename': entry}
        # Add additional metadata dictionary items in form 'Next_field': ''  The values
        # for these additional metadata fields can be updated later by their individual keys.
print('Found ', len(subject_metadata), ' files to upload in this directory.')

set_name = input('Entry a name for the subject set to use or create:' + '\n')
previous_subjects = []

try:
    # check if the subject set already exits
    subject_set = SubjectSet.where(project_id=project.id, display_name=set_name).next()
    print('You have chosen to upload ', len(subject_metadata), ' files to an existing subject set',  set_name)
    retry = input('Enter "n" to cancel this upload, any other key to continue' + '\n')
    if retry.lower() == 'n':
        quit()
    for subject in subject_set.subjects:
        previous_subjects.append(subject.metadata['Filename'])
except StopIteration:
    print('You have chosen to upload ', len(subject_metadata), ' files to an new subject set ',  set_name)
    retry = input('Enter "n" to cancel this upload, any other key to continue' + '\n')
    if retry.lower() == 'n':
        quit()
    # create a new subject set for the new data and link it to the project above
    subject_set = SubjectSet()
    subject_set.links.project = project
    subject_set.display_name = set_name
    subject_set.save()

print('Uploading subjects, this could take a while!')
new_subjects = 0
for filename, metadata in subject_metadata.items():
    try:
        if filename not in previous_subjects:
            subject = Subject()
            subject.links.project = project
            subject.add_location(location + os.sep + filename)
            subject.metadata.update(metadata)
            subject.save()
            subject_set.add(subject.id)
            print(filename)
            new_subjects += 1
    except panoptes_client.panoptes.PanoptesAPIException:
        print('An error occurred during the upload of ', filename)
print(new_subjects, 'new subjects created and uploaded')

uploaded = 0
with open(location + os.sep + 'Uploaded subjects.csv', 'wt') as file:
    subject_set = SubjectSet.where(project_id=project.id, display_name=set_name).next()
    for subject in subject_set.subjects:
        uploaded += 1
        file.write(subject.id + ',' + list(subject.metadata.values())[0] + '\n')
    print(uploaded, ' subjects found in the subject set, see the full list in Uploaded subjects.csv.')
