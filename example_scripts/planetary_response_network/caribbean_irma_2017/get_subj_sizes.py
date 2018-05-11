# REQUIRES python 3 if you're going to get image sizes from the URLs
import sys, os
import numpy as np
import pandas as pd
import ujson
import scipy.interpolate
import scipy.ndimage
from pyproj import Proj, transform
import urllib
from PIL import ImageFile
from ast import literal_eval

project_name = "planetary-response-network-and-rescue-global-caribbean-storms-2017"

#active_subject_sets = [14709, 14710, 14750, 14746]
#active_subject_sets = [14750, 14746]
#active_subject_sets = [14770]
#active_subject_sets = [14773]
#active_subject_sets = [14759]
#active_subject_sets = [14806]
#active_subject_sets = [14813]
active_subject_sets = [14929]
active_subject_sets = [14827]
active_subject_sets = [14896] # Barbuda
# also 14930 - Antigua
#active_subject_sets = [14709, 14710, 14746, 14750, 14759, 14764, 14770, 14773]

try:
    infile = sys.argv[1]
except:
    infile    = "%s-classifications.csv" % project_name

try:
    active_subject_sets = literal_eval(sys.argv[2])
except:
    try:
        active_subject_sets = [int(sys.argv[2])]
    except:
        pass


ssid_str = '%d' % active_subject_sets[0]
for i in range(len(active_subject_sets)):
    if i > 0:
        ssid_str = '%s_%d' % (ssid_str, active_subject_sets[i])


workflow_file = "%s-workflows.csv"       % project_name
workflow_contents_file = "%s-workflow_contents.csv" % project_name
subjectfile   = "%s-subjects.csv" % project_name
subjectfile_out = subjectfile.replace(".csv", "_enhancedinfo_ssids_%s.csv" % ssid_str)

# these files will/may be written to
outfile      = "%s-marks-points.csv" % project_name
blankfile    = "%s-marks-blank.csv"  % project_name
shortcutfile = "%s-marks-unclassifiable.csv"  % project_name


# Guadeloupe
workflow_id = 4928
workflow_version = "18.53"

# Turks and Caicos - Landsat 8
workflow_id = 4970
workflow_version = "5.8"

# digital globe
workflow_id = 4958
workflow_version = "17.60"

# planet labs
#workflow_id = 4975
#workflow_version = "1.1"

# building counts only
workflow_id = 5030
workflow_version = 3.8




def get_projection(ssid):
    landsat_ssids = [14770, 14773]

    if (ssid in landsat_ssids):
        return Proj(init='epsg:32618')
    else:
        # this is for Sentinel 2 and others
        return Proj(init='epsg:32620')


# takes a single metadata row
def get_corner_latlong(meta_json, ssid):
    # in some cases we've included the corner lat and long in the metadata, in other cases not quite, but we can get that info
    # recall that longitude is the x direction, latitude is the y direction
    # BDS-created subjects have min and max lat and long so we can read it directly
    try:
        lon_min = meta_json['lon_min']
        lon_max = meta_json['lon_max']
        lat_min = meta_json['lat_min']
        lat_max = meta_json['lat_max']
    except:
        # some of the subjects have the corners given in unprojected units
        # which are in meters, but with actual value set by a global grid
        x_m_min = meta_json['#tile_UL_x']
        y_m_max = meta_json['#tile_UL_y']
        x_m_max = meta_json['#tile_LR_x']
        y_m_min = meta_json['#tile_LR_y']

        #print(meta_json)
        #print((x_m_min, y_m_min, x_m_max, y_m_max))

        #f_x_lon, f_y_lat = get_interp_grid(subjects, ssid)
        inProj = get_projection(ssid)
        outProj = Proj(init='epsg:4326')

        lon_min, lat_min = transform(inProj,outProj,x_m_min,y_m_min)
        lon_max, lat_max = transform(inProj,outProj,x_m_max,y_m_max)

        #print((lon_min, lat_min, lon_max, lat_max))
        #print("\n")

    return lon_min, lon_max, lat_min, lat_max

# supposedly gets the dimensions of an image from the web without having to download the whole thing
# we will see
# https://stackoverflow.com/questions/7460218/get-image-size-without-downloading-it-in-python
def getsizes(subject):

    # if it already exists just return it back
    try:
        return None, (subject['imsize_x_pix'], subject['imsize_y_pix'])
    except:
        try:
            return None, (subject[1]['meta_json']['imsize_x_pix'], subject[1]['meta_json']['imsize_y_pix'])
        except:
            #print("You shouldn't be here")
            uri = subject[1]['loc_im0']
            # get file size *and* image size (None if not known)
            file = urllib.request.urlopen(uri)
            size = file.headers.get("content-length")
            if size:
                size = int(size)
            p = ImageFile.Parser()
            while True:
                data = file.read(1024)
                if not data:
                    break
                p.feed(data)
                if p.image:
                    return size, p.image.size
                    break
            file.close()
            return size, None



subjects_all = pd.read_csv(subjectfile)
is_active = np.array([q in active_subject_sets for q in subjects_all.subject_set_id])
in_workflow = subjects_all.workflow_id == workflow_id
subjects = (subjects_all[is_active & in_workflow]).copy()

print("There are %s subjects in this subject set/workflow combination." % len(subjects))

subjects['meta_json'] = [ujson.loads(q) for q in subjects.metadata]
subjects['loc_json']  = [ujson.loads(q) for q in subjects.locations]
subjects['loc_im0']   = [q['0'] for q in subjects.loc_json]
try:
    subjects['loc_im1']   = [q['1'] for q in subjects.loc_json]
except:
    pass
    # some subjects only have one image

print("Getting image corner coordinates...")
coords = [get_corner_latlong(q, active_subject_sets[0]) for q in subjects['meta_json']]
#lon_min, lon_max, lat_min, lat_max
subjects['lon_min'] = [q[0] for q in coords]
subjects['lon_max'] = [q[1] for q in coords]
subjects['lat_min'] = [q[2] for q in coords]
subjects['lat_max'] = [q[3] for q in coords]

print("Fetching image sizes...")
sizes = [getsizes(q) for q in subjects.iterrows()]

subjects['filesize_bytes'] = [q[0] for q in sizes]
subjects['imsize_x_pix'] = [q[1][0] for q in sizes]
subjects['imsize_y_pix'] = [q[1][1] for q in sizes]

cols_out = subjects.columns.values.tolist()
# these will just print as exact duplicates of the metadata and locations columns
# plus they're often quite long, so, don't print them
cols_out.remove('meta_json')
cols_out.remove('loc_json')

subjects[cols_out].to_csv(subjectfile_out)
print("  output written to %s ." % subjectfile_out)
#end
