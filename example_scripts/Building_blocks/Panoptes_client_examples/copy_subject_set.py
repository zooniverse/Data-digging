import os
import csv
import sys
from panoptes_client import SubjectSet, Project, Panoptes

csv.field_size_limit(sys.maxsize)

# connect to Panoptes_Client Note Os environment variables must be set! Else use the commented
# out line with your user_name and password hardcoded (in this case keep the code secure!).
# Panoptes.connect(username='user_name', password='password')
Panoptes.connect(username=os.environ['User_name'], password=os.environ['Password'])

# get source project id and existing subject set name
while True:
    proj_id = input('Enter the project id for the subject set to copy:' + '\n')
    set_name = input('Enter a name for the subject set to copy:' + '\n')
    try:
        subject_set_old = SubjectSet.where(project_id=proj_id, display_name=set_name).next()
        break
    except:
        print('subject set not found or not accessible')
        subject_set_old = ''
        retry = input('Enter "y" to try again, any other key to exit' + '\n')
        if retry.lower() != 'y':
            quit()

#  build list of subjects in source subject set
add_subjects = []
for subject in subject_set_old.subjects:
    add_subjects.append(subject.id)
print(len(add_subjects), ' subjects found in the subject set to copy')

# get project id of destination project;
while True:
    proj_id = input('Enter the project id for the new subject set:' + '\n')
    try:
        proj = Project.find(proj_id)
        break
    except:
        print('Project not found or accessible')
        retry = input('Enter "y" to try again, any other key to exit' + '\n')
        if retry.lower() != 'y':
            quit()

#  get new subject name
new_set_name = input('Enter a name for the subject set to use or create:' + '\n')

# find or build destination subject set
try:
    # check if the subject set already exits
    subject_set_new = SubjectSet.where(project_id=proj.id, display_name=new_set_name).next()
except:
    # create a new subject set for the new data and link it to the project above
    subject_set_new = SubjectSet()
    subject_set_new.links.project = proj
    subject_set_new.display_name = new_set_name
    subject_set_new.save()

#  iterate through the subjects linking them and verifying they link.
k = 0
for sub in add_subjects:
    try:
        subject_set_new.add(sub)
        print(sub, 'linked to new set')
        k += 1
    except:
        print(sub,  'previously linked or did not link correctly')
print(k, ' subjects linked to subject set ', new_set_name, ' in project ', proj_id)

linked = 0
with open(os.getcwd() + os.sep + 'copied_subjects.csv', 'wt') as file:
    subject_set = SubjectSet.where(project_id=proj_id, display_name=new_set_name).next()
    for subject in subject_set.subjects:
        linked += 1
        file.write(subject.id + '\n')
print(linked, ' subjects found in the new subject set, see the full list in copied subjects.csv.')
