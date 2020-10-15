from panoptes_client import Panoptes, SubjectSet, Subject

###################################

### Subject Deletion Script
# USE WITH CAUTION! Once deleted, subjects are not recoverable!

# Input Parameters

# Login Credentials
puser = <ZOONIVERSE_USERNAME>
ppswd = <ZOONIVERSE_PASSWORD>

# Operate on subjects in `subject_set_id` with IDs between
# limit_lo_subjectid and limit_hi_subjectid (inclusive).
subject_set_id = 999999
limit_lo_subjectid = 31000000
limit_hi_subjectid = 38000000

do_print_list = True
do_deletion = False

###################################

Panoptes.connect(username=puser, password=ppswd)

### Construct list of IDs for subjects that need deletion

# Select range of subject IDs from those in a given subject set
subject_set = SubjectSet.find(subject_set_id)
subject_ids = []
for subject in subject_set.subjects:
    # Use Subject ID ranges to help narrow down subset for deletion
    if ((int(subject.id) >= limit_lo_subjectid) & (int(subject.id) <= limit_hi_subjectid)):
        subject_ids.append(int(subject.id))

# Optional: verify subject ID list before running deletion
if do_print_list:
    print(subject_ids)
    print('Number of subjects found: {}'.format(len(subject_ids)))
        
# Perform deletion
if do_deletion:
    for s in subject_ids:
        Subject.find(s).delete()
