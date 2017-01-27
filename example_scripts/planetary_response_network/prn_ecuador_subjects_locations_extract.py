import sys, os, csv, json
import numpy as np
importn pandas as pd
from ast import literal_eval

'''
This file will break the raw classifications from the PRN Ecuador (2016) project out into a csv file with individual markings, including a file that shows the lat/long of the markings (based on reading the subject data, which included geocoords, and interpolating those to find the geoboundaries of markings). The markings are rectangles.

The program also outputs a list of URLs to link to the before/after photos that make up each subject.
'''

def get_structural(row):
    if "Structural" in row:
        return 1.
    else:
        return 0.

def get_road(row):
    if "Road" in row:
        return 1.
    else:
        return 0.

def get_cloud(row):
    if "Thick" in row:
        return 1.
    else:
        return 0.

def get_missing(row):
    if "Missing" in row:
        return 1.
    else:
        return 0.



#q['annotations_json'][0]['value'][i]['tool_label']
#                         ^ it might break here
#                                  ^ or here
# ugh, no, this only works on the original workflow
def get_markings_id(row):

    #extract the markings (while loop)
    the_marks='['
    try:
        n_markings = len(row[0]['value'])
        i=0
        while i < n_markings:
            try:
                label = row[0]['value'][i]['tool_label']
                if len(the_marks) < 2:
                    the_marks += "'"+label+"'"
                else:
                    the_marks += ",'"+label+"'"
            except:
                pass
            i+=1
        the_marks += ']'
    except:
        the_marks += ']'

    the_marks_list = pd.Series(literal_eval(the_marks)).unique()

    return the_marks_list


#q['annotations_json'][0]['value'][i]['tool_label']
#                         ^ it might break here
#                                  ^ or here
def get_subject_id(row):

    #extract the subject_id
    try:
        subject_id = int(str(row.keys())[12:19])
    except:
        subject_id = -1



    return subject_id







# Note the user_name still has the IP address in it if the user is not logged in;
# so this is just to be sure (in case the IP isn't unique)
def get_alternate_sessioninfo(row):

    # if they're logged in, save yourself all this trouble
    if not row[1]['user_name'].startswith('not-logged-in'):
        return row[1]['user_name']
    else:
        metadata = row[1]['class_metadata_json']
        # IP + session, if it exists
        # (IP, agent, viewport_width, viewport_height) if session doesn't exist
        try:
            # start with "not-logged-in" so stuff later doesn't break
            return str(row[1]['user_name']) +"_"+ str(metadata['session'])
        except:
            try:
                viewport = str(metadata['viewport'])
            except:
                viewport = "NoViewport"

            try:
                user_agent = str(metadata['user_agent'])
            except:
                user_agent = "NoUserAgent"

            try:
                user_ip = str(row[1]['user_name'])
            except:
                user_ip = "NoUserIP"

            thesession = user_ip + user_agent + viewport
            return thesession


#################################################################################
#################################################################################
#################################################################################


subj_raw = pd.read_csv('planetary-response-network-and-rescue-global-ecuador-earthquake-2016-subjects.csv')

classifications = pd.read_csv('planetary-response-network-and-rescue-global-ecuador-earthquake-2016-classifications.csv')

# In [6]: subj_raw.columns
# Out[6]:
# Index(['subject_id', 'project_id', 'workflow_ids', 'subject_set_id',
#        'metadata', 'locations', 'classifications_by_workflow',
#        'retired_in_workflow'],
#       dtype='object')
subj_raw['metadata_json'] = [json.loads(q) for q in subj_raw.metadata]
subj_raw['locations_json'] = [json.loads(q) for q in subj_raw.locations]

classifications['annotations_json'] = [json.loads(q) for q in classifications.annotations]
classifications['class_metadata_json'] = [json.loads(q) for q in classifications.metadata]
classifications['subject_json'] = [json.loads(q) for q in classifications.subject_data]

classifications['user_label'] = [get_alternate_sessioninfo(q) for q in classifications['user_name class_metadata_json'.split()].iterrows()]

classifications['subject_id'] = [get_subject_id(q) for q in classifications['subject_json']]
classifications['objects_marked'] = [get_markings_id(q) for q in classifications['annotations_json']]

classifications['struct_damage'] = [get_structural(q) for q in classifications.annotations]
classifications['road_blocked']  = [get_road(q) for q in classifications.annotations]
classifications['missing_image'] = [get_missing(q) for q in classifications.annotations]
classifications['thick_cloud']   = [get_cloud(q) for q in classifications.annotations]
classifications['ones'] = classifications.thick_cloud * 0.0 + 1.0

by_subj = classifications.groupby('subject_id')
n_struct  = by_subj.struct_damage.aggregate('sum')
n_road    = by_subj.road_blocked.aggregate('sum')
n_missing = by_subj.missing_image.aggregate('sum')
n_cloud   = by_subj.thick_cloud.aggregate('sum')
n_tot     = by_subj.ones.aggregate('sum')

f_struct  = n_struct/n_tot
f_road    = n_road/n_tot
f_missing = n_missing/n_tot
f_cloud   = n_cloud/n_tot

subj_class_f = pd.DataFrame(f_struct)
subj_class_f.columns = ['f_struct']
subj_class_f['f_road']    = f_road
subj_class_f['f_missing'] = f_missing
subj_class_f['f_cloud']   = f_cloud
subj_class_f['n_tot']     = n_tot
subj_class_f['subject_id'] = subj_class_f.index

subj_raw['before_loc'] = [q['1'] for q in subj_raw.locations_json]
subj_raw['after_loc'] = [q['0'] for q in subj_raw.locations_json]

subj_raw['after_loc'] = [q['0'] for q in subj_raw.locations_json]
subj_raw['is_blank'] = [False for q in subj_raw.subject_id]

subj_raw['image1'] = [q['image2'] for q in subj_raw.metadata_json]
subj_raw['image2'] = [q['image1'] for q in subj_raw.metadata_json]
subj_raw['center_lat'] = [q['center_lat'] for q in subj_raw.metadata_json]
subj_raw['center_lon'] = [q['center_lon'] for q in subj_raw.metadata_json]
subj_raw['bottom_right_lat'] = [q['bottom_right_lat'] for q in subj_raw.metadata_json]
subj_raw['bottom_right_lon'] = [q['bottom_right_lon'] for q in subj_raw.metadata_json]
subj_raw['upper_right_lat'] = [q['upper_right_lat'] for q in subj_raw.metadata_json]
subj_raw['upper_right_lon'] = [q['upper_right_lon'] for q in subj_raw.metadata_json]
subj_raw['bottom_left_lat'] = [q['bottom_left_lat'] for q in subj_raw.metadata_json]
subj_raw['bottom_left_lon'] = [q['bottom_left_lon'] for q in subj_raw.metadata_json]
subj_raw['upper_left_lat'] = [q['upper_left_lat'] for q in subj_raw.metadata_json]
subj_raw['upper_left_lon'] = [q['upper_left_lon'] for q in subj_raw.metadata_json]




subj_raw['subject_id subject_set_id before_loc after_loc is_blank'.split()].to_csv('prn_ecuador_subjects_locations_only_presifting.csv')

subjects = subj_raw['subject_id subject_set_id image1 image2 center_lat center_lon upper_left_lat upper_left_lon upper_right_lat upper_right_lon bottom_right_lat bottom_right_lon bottom_left_lat bottom_left_lon before_loc after_loc'.split()]
subjects.to_csv('prn_subjects_lat_long_images.csv')

subj_w_class = pd.merge(subjects, subj_class_f, how='left', on='subject_id', sort=False, suffixes=('_2', ''), copy=True)

subj_w_class.to_csv('prn_subjects_lat_long_images_classifications.csv')


class_needed = classifications['classification_id subject_id user_name user_label user_id user_ip workflow_id workflow_name workflow_version created_at struct_damage road_blocked thick_cloud missing_image'.split()]



class_subj = pd.merge(class_needed, subj_w_class, how='left',
                               on='subject_id',
                               sort=False, suffixes=('_2', ''), copy=True)

class_subj.to_csv('classifications_withsubjects_abbreviated_markings.csv')
