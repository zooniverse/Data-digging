#!/usr/bin/env python

from panoptes_client import Panoptes, SubjectSet, Subject
import urllib.request
import os

#################
# INPUT PARAMS

# Input and Output Values
subject_set_id = 94047 # Subject Set ID
dir_imgraw = 'imgraw_94047' # Destination for images

# Zooniverse Login
puser = 'USERNAME'
ppswd = 'PASSWORD'

#################
# SCRIPT CODE

Panoptes.connect(username=puser, password=ppswd)

if not os.path.exists(dir_imgraw):
    os.makedirs(dir_imgraw)

ss = SubjectSet.find(subject_set_id)

for s in ss.subjects:
    
    n_frames = len(s.locations)

    for index,loc in enumerate(s.locations):
        if n_frames == 1:
            imfile = dir_imgraw+'/{}.jpg'.format(s.id)
        else:
            imfile = dir_imgraw+'/{}_{}.jpg'.format(s.id,index)
        while not os.path.exists(imfile):
            try:
                for img_mimetype,img_url in loc.items():
                    urllib.request.urlretrieve(img_url, imfile)
            except urllib.error.HTTPError as exception:
                print('ERROR - '+s.id+': '+str(exception.reason))
