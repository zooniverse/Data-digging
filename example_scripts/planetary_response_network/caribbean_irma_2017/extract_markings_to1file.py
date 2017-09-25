import sys, os
import numpy as np
import pandas as pd
import ujson
from scipy.interpolate import interp1d
import scipy.ndimage



from get_workflow_info import get_workflow_info

project_name = "planetary-response-network-and-rescue-global-caribbean-storms-2017"

# st thomas DG
#ssid = 14759

# St John DG
ssid = 14806

# St John Planet
#ssid = 14813

# Puerto Rico before only
#ssid = 14929

# Turks and Caicos Cockburn Town DG/Planet
ssid = 14827

# DG - Barbuda
ssid = 14896

# DG - Antigua
ssid = 14930

# Planet - Dominica
ssid = 14988

#infile    = "%s-classifications.csv" % project_name

#infile = 'damage-floods-blockages-shelters-landsat-classifications.csv'
infile = 'damage-floods-blockages-shelters-classifications.csv'
#infile = 'damages-floods-blockages-shelters-planet-labs-classifications.csv'
#infile = 'planetary-response-network-and-rescue-global-caribbean-storms-2017-classifications_wfid4958_nodups_inclnonlive.csv'

try:
    infile = sys.argv[1]
except:
    pass

workflow_version = -1
workflow_id = 4958
freetext = ''
outdir = "outfiles"
# check for other command-line arguments
if len(sys.argv) > 1:
    # if there are additional arguments, loop through them
    for i_arg, argstr in enumerate(sys.argv[1:]):
        arg = argstr.split('=')

        if (arg[0] == "workflow_id") | (arg[0] == "wfid"):
            workflow_id = int(arg[1])
        elif (arg[0] == "workflow_version") | (arg[0] == "wfv"):
            workflow_version = arg[1]
        elif (arg[0] == "subject_set_id") | (arg[0] == "ssid"):
            ssid = int(arg[1])
        elif (arg[0] == "name") | (arg[0] == "stub") | (arg[0] == "freetext"):
            freetext = arg[1]
        elif (arg[0] == "outdir"):
            outdir = arg[1]


workflow_file = "%s-workflows.csv"       % project_name
workflow_contents_file = "%s-workflow_contents.csv" % project_name
# if this subject file doesn't already exist, run get_subject_sizes.py
# note it has to download images to determine imsize (in pixels) so generate it some
# other way if you already have that info
subjectfile   = "%s-subjects_enhancedinfo_ssids_%d.csv" % (project_name, ssid)

# these files will/may be written to
outfile_nodir      = "%s-marks-points_wfid_%d.csv" % (project_name, workflow_id)
blankfile_nodir    = "%s-marks-blank_wfid_%d.csv"  % (project_name, workflow_id)
shortcutfile_nodir = "%s-marks-unclassifiable_wfid_%d.csv"  % (project_name, workflow_id)
questionfile_nodir = "%s-questions_wfid_%d.csv"  % (project_name, workflow_id)

outfile      = "%s/%s" % (outdir, outfile_nodir)
blankfile    = "%s/%s" % (outdir, blankfile_nodir)
shortcutfile = "%s/%s" % (outdir, shortcutfile_nodir)
questionfile = "%s/%s" % (outdir, questionfile_nodir)


# the order of tools is from the workflow information - as is the fact the
# marks are in task T2
tools = ['Road Blockage', 'Flood', 'Temporary Settlement', 'Structural Damage']
mark_count = [0, 0, 0, 0]


shortcuts = ['Unclassifiable Image', 'Ocean Only (no land)']
shortcut_mark_count = [0, 0]


# for the structural damage subtask, if it exists
details = ['Minor', 'Moderate', 'Catastrophic']







def get_wf_basics(workflow_id):
    # I should be able to do this marking_tasks, shortcuts, questions etc
    # automatically from workflow_info BUT NOT RIGHT NOW
    # Guadeloupe
    if workflow_id == 4928:
        workflow_version = '18.53'
        marking_tasks = ['T0']
        question_tasks = ['']
        shortcut_tasks = ['T1']
        struc_subtask = False

    # Turks and Caicos - Landsat 8
    elif workflow_id == 4970:
        workflow_version = '5.8'
        marking_tasks = ['T0']
        question_tasks = ['T2']
        shortcut_tasks = ['T1', 'T3']
        struc_subtask = False


    # St Thomas - Digital Globe
    # also anything that uses DG
    elif workflow_id == 4958:
        workflow_version = '17.60'
        marking_tasks = ['T0']
        question_tasks = ['T2']
        shortcut_tasks = ['T1', 'T3']
        struc_subtask = True

    # Clone of the DG workflow but for Planet data
    elif workflow_id == 4975:
        workflow_version = '1.1'  # could also be 2.2 if Dominica or later
        marking_tasks = ['T0']
        question_tasks = ['T2']
        shortcut_tasks = ['T1', 'T3']
        #struc_subtask = True # even though I doubt these are trustworthy
        struc_subtask = False

    # Puerto Rico before only
    elif workflow_id == 5030:
        workflow_version = '3.8'
        marking_tasks = []
        question_tasks = ['T2']
        shortcut_tasks = ['T1', 'T3']
        struc_subtask = False

    return workflow_version, marking_tasks, question_tasks, shortcut_tasks, struc_subtask





def get_coords_mark(markinfo):

    row = markinfo[1]
    # print(markinfo)
    # print("-----")
    # print(row)
    # print("\n\n")

    mark_x = row['x']
    mark_y = row['y']

    the_x = np.array([row['x_min'], row['imsize_x_pix']])
    the_y = np.array([row['y_min'], row['imsize_y_pix']])
    the_lon = np.array([row['lon_min'], row['lon_max']])
    the_lat = np.array([row['lat_min'], row['lat_max']])

    # don't throw an error if the coords are out of bounds, but also don't extrapolate
    f_x_lon = interp1d(the_x, the_lon, bounds_error=False, fill_value=(None, None))
    f_y_lat = interp1d(the_y, the_lat, bounds_error=False, fill_value=(None, None))

    return f_x_lon(mark_x), f_y_lat(mark_y)




def get_projection(ssid):
    # for now let's just return the same projection for everything
    # this is for Sentinel 2
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



wfv, marking_tasks, question_tasks, shortcut_tasks, struc_subtask = get_wf_basics(workflow_id)
# don't overwrite the workflow version if it's specified at the prompt
if workflow_version < 1:
    workflow_version = wfv

# okay turns out we didn't really need this but I'm hoping it will make it easier to generalize later
workflow_df  = pd.read_csv(workflow_file)
workflow_cdf = pd.read_csv(workflow_contents_file)
workflow_info = get_workflow_info(workflow_df, workflow_cdf, workflow_id, workflow_version)





classifications_all = pd.read_csv(infile)

classifications_all['anno_json'] = [ujson.loads(q) for q in classifications_all['annotations']]

# it's either True or it's blank, so change the blanks to explicitly False
classifications_all['gs'] = np.array(classifications_all.gold_standard, dtype=bool)

# only use classifications from the workflow & version we care about
classifications_all['workflow_major'] = [int(q) for q in classifications_all.workflow_version]
workflow_version_major = int((workflow_version.split('.'))[0])
in_workflow = classifications_all.workflow_major == workflow_version_major

classifications = classifications_all[in_workflow]


'''
I noticed during a previous project that pandas (I think it was pandas
and not some more fundamental property of python itself?) seemed *very*
slow when trying to build a large dataframe or series of marks and then write
the whole thing to a file in one go. For a project with lots of classifications
it will be much faster to write line-by-line to a csv file and then, if needed,
read in the csv file at the end of the loop through the classifications.

'''

# these are unnecessary if you're running this from a prompt but if you're copy-pasting in iPython they're needed so things below don't break
try:
    del fmarks
except:
    pass

try:
    del fempty
except:
    pass

try:
    del fquest
except:
    pass

# all markers for this project are a point so we're putting them all in the same file
# likewise for the question task - there's just one so put everything in 1 file
# we'll assume there is at least 1 mark and 1 question answer in the project so that this file will not end up empty
# if we're wrong it won't crash, it'll just be a file with only a header line
# (we don't make that assumption with the blanks file, so we only open/write to it if it's needed)
fmarks = open(outfile, "w")
fquest = open(questionfile, "w")

# write the header line for the file
# file has the basic classification information + the mark information
# including sanity check stuff + stuff we may never need, like the tool number
# and the frame the user drew the mark on, respectively

# all markers are a point: {(x, y)}
if struc_subtask:
    fmarks.write("mark_id,classification_id,subject_id,created_at,user_name,user_id,user_ip,tool,label,how_damaged,frame,x,y\n")
else:
    fmarks.write("mark_id,classification_id,subject_id,created_at,user_name,user_id,user_ip,tool,label,frame,x,y\n")

fquest.write("classification_id,subject_id,created_at,user_name,user_id,user_ip,question,label,gold_standard\n")



# now extract the marks from each classification
# people who say Python should never need for loops are either way better at it
# than I am or have never dealt with Zooniverse classification exports
# (or both)
i_empty = 0
i_mark = 0
i_shortcut = 0
i_question = 0
i_exception = 0
exception_rows = []
for i, row in enumerate(classifications.iterrows()):
    # row[0] is the index, [1] is the classification info
    cl = row[1]

    class_id   = cl['classification_id']
    subject_id = cl['subject_ids']
    created_at = cl['created_at']
    username   = cl['user_name']
    userid     = cl['user_id']
    userip     = cl['user_ip']
    is_gs      = cl['gs']

    # for anonymous users the userid field is blank so reads as NaN
    # which will throw an error later
    if np.isnan(userid):
        userid = -1

    # loop through annotations in this classification
    # (of which there can be arbitrarily many)
    for j, anno in enumerate(cl['anno_json']):

        thetask  = anno['task']
        #thelabel = anno['task_label']

        if thetask in marking_tasks:

            #tool_label = anno['tool_label']

            # first, if this classification is blank, just write the basic information
            # this will keep track of classifications where the user said there was nothing there
            # these may be important for some user weighting schemes etc.
            if len(anno['value']) < 1:
                i_empty+=1
                try:
                    # this will be fine for every empty mark except the first one
                    fempty.write("%d,%d,\"%s\",\"%s\",%d,%s\n" % (class_id, subject_id, created_at, username, userid, userip))
                except:
                    # if the file isn't already opened, open it and write a header
                    fempty = open(blankfile, "w")
                    # the blank table just needs the classification information
                    fempty.write("classification_id,subject_id,created_at,user_name,user_id,user_ip\n")
                    fempty.write("%d,%d,\"%s\",\"%s\",%d,%s\n" % (class_id, subject_id, created_at, username, userid, userip))

            else:
                # it's not empty, so let's collect other info
                # the marks themselves are in anno['value'], as a list
                for i_v, thevalue in enumerate(anno['value']):

                    # how we write to the file (and which file) depends on which tool
                    # is being used
                    #
                    # the annotation json returns an integer that's the index of the
                    # tools array we defined earlier
                    # obviously I could just use the integer but this is easier to read
                    # so worry about string vs int compare speeds when you have many
                    # millions of classifications

                    try:
                        thetool = tools[thevalue['tool']]
                        is_exception = False
                    except:
                        is_exception = True
                        i_exception += 1
                        exception_rows.append(row[0])

                    # I'm not just putting everything below inside the try statement because
                    # if something else here crashes, I want it to shout at me
                    # failing silently is BAD in aggregation
                    if not is_exception:
                        i_mark+=1
                        thedeets = ''

                        #'Road Blockage', 'Flood', 'Temporary Settlement', 'Structural Damage'
                        if thetool == "Road Blockage":
                            mark_count[0] += 1
                            how_damaged = ''

                        if thetool == "Flood":
                            mark_count[1] += 1
                            how_damaged = ''

                        if thetool == "Temporary Settlement":
                            mark_count[2] += 1
                            how_damaged = ''

                        if thetool == "Structural Damage":
                            mark_count[3] += 1
                            how_damaged = ''
                            if struc_subtask:
                                # filling this in is optional
                                if thevalue['details'][0]['value'] is None:
                                    thedeets = 'Not Given'
                                else:
                                    thedeets = details[thevalue['details'][0]['value']]



                        if thetool in tools:
                            if struc_subtask:
                                fmarks.write("%d,%d,%d,\"%s\",\"%s\",%d,%s,%d,\"%s\",\"%s\",%d,%.2f,%.2f\n" % (i_mark, class_id, subject_id, created_at, username, userid, userip, thevalue['tool'], thetool, thedeets, thevalue['frame'], thevalue['x'], thevalue['y']))
                            else:
                                fmarks.write("%d,%d,%d,\"%s\",\"%s\",%d,%s,%d,\"%s\",%d,%.2f,%.2f\n" % (i_mark, class_id, subject_id, created_at, username, userid, userip, thevalue['tool'], thetool, thevalue['frame'], thevalue['x'], thevalue['y']))



        if thetask in question_tasks:
            i_question+=1
            # we currently only have single-answer-permitted question tasks so we don't need to loop through values
            thevalue = anno['value']
            theslug  = workflow_info[thetask]['question_slug']
            #print("%d,%d,\"%s\",\"%s\",%d,%s,\"%s\",\"%s\"" % (class_id, subject_id, created_at, username, userid, userip, theslug, thevalue))
            try:
                # this will be fine for every shortcut mark except the first one
                fquest.write("%d,%d,\"%s\",\"%s\",%d,%s,\"%s\",\"%s\"\n" % (class_id, subject_id, created_at, username, userid, userip, theslug, thevalue))
            except:
                # if the file isn't already opened, open it and write a header
                fquest = open(questionfile, "w")
                # the blank table just needs the classification information
                fquest.write("classification_id,subject_id,created_at,user_name,user_id,user_ip,question,label,gold_standard\n")
                fquest.write("%d,%d,\"%s\",\"%s\",%d,%s,\"%s\",\"%s\"\n" % (class_id, subject_id, created_at, username, userid, userip, theslug, thevalue))



        if thetask in shortcut_tasks:
            i_shortcut+=1
            for i_v, thevalue in enumerate(anno['value']):
                try:
                    # this will be fine for every shortcut mark except the first one
                    fshortcut.write("%d,%d,\"%s\",\"%s\",%d,%s,\"%s\",%r\n" % (class_id, subject_id, created_at, username, userid, userip, thevalue, is_gs))
                except:
                    # if the file isn't already opened, open it and write a header
                    fshortcut = open(shortcutfile, "w")
                    # the blank table just needs the classification information
                    fshortcut.write("classification_id,subject_id,created_at,user_name,user_id,user_ip,label,gold_standard\n")
                    fshortcut.write("%d,%d,\"%s\",\"%s\",%d,%s,\"%s\",%r\n" % (class_id, subject_id, created_at, username, userid, userip, thevalue, is_gs))




fmarks.close()
try:
    fempty.close()
except:
    pass

try:
    fshortcut.close()
except:
    pass

try:
    fquest.close()
except:
    pass

print("Saved %d marks from %d classifications (of which %d were empty and %s were shortcuts) to %s." % (i_mark, len(classifications), i_empty, i_shortcut, outfile))
print("Saved %d questions from %d classifications to %s." % (i_question, len(classifications), questionfile))
print("Mark breakdown: Road Blockage %d, Flood %d, Temp Settlement %d, Structural damage %d\n" % tuple(mark_count))


# now read in those mark files and match them to subjects
print("Matching to subjects in %s ..." % subjectfile)

subjects_all = pd.read_csv(subjectfile)
#active_subject_sets = [14709, 14710, 14746, 14750, 14759, 14764, 14770, 14773, 14806, 14813, 14929]
active_subject_sets = [ssid]
is_active = np.array([q in active_subject_sets for q in subjects_all.subject_set_id])
#in_workflow = subjects_all.workflow_id == workflow_id
#subjects = (subjects_all[is_active & in_workflow]).copy()
subjects = (subjects_all[is_active]).copy()

if len(subjects) > 0:

    subjects['meta_json'] = [ujson.loads(q) for q in subjects.metadata]
    # this should all already be there
    # subjects['loc_json']  = [ujson.loads(q) for q in subjects.locations]
    # subjects['loc_im0']   = [q['0'] for q in subjects.loc_json]
    #
    # coords = [get_corner_latlong(q, 14710) for q in subjects['meta_json']]
    # #lon_min, lon_max, lat_min, lat_max
    # subjects['lon_min'] = [q[0] for q in coords]
    # subjects['lon_max'] = [q[1] for q in coords]
    # subjects['lat_min'] = [q[2] for q in coords]
    # subjects['lat_max'] = [q[3] for q in coords]

    ################################## matching marks
    # read in the mark file we've just written
    if i_mark > 0:
        themarks = pd.read_csv(outfile)

        # match the marks to the subjects by subject ID
        marks_subj = pd.merge(themarks, subjects, how='left', on='subject_id', suffixes=('', '_2'))

        # now we have marks in pixel coordinates and we have the corner coordinates in both x,y and lon, lat

        marks_subj['x_min'] = np.ones_like(marks_subj.subject_id)
        marks_subj['y_min'] = np.ones_like(marks_subj.subject_id)

        marks_coords = [get_coords_mark(q) for q in marks_subj.iterrows()]
        marks_subj['lon_mark'] = np.array([q[0] for q in marks_coords], dtype=float)
        marks_subj['lat_mark'] = np.array([q[1] for q in marks_coords], dtype=float)

        in_bounds = np.invert(np.isnan(marks_subj['lon_mark'])) & np.invert(np.isnan(marks_subj['lat_mark']))

        marks_subj_clean = marks_subj[in_bounds]

        # columns we'd like to save in the subjects, in save order
        subj_cols_out = [u'lon_min', u'lon_max', u'lat_min', u'lat_max', u'filesize_bytes', u'imsize_x_pix', u'imsize_y_pix', 'subject_set_id', 'locations', 'classifications_count', 'retired_at', 'retirement_reason', 'metadata']

        #themarks.set_index('mark_id', inplace=True)

        # save all columns from the mark file
        mark_cols_out = (themarks.columns.values).tolist()

        # columns based on the intersection of these
        markcoords_cols = ['lon_mark', 'lat_mark']

        all_cols_out = mark_cols_out + markcoords_cols + subj_cols_out

        outfile_wsubj = "%s/%s%s" % (outdir, freetext, outfile_nodir.replace(".csv", "-wsubjinfo.csv"))

        marks_subj_clean[all_cols_out].to_csv(outfile_wsubj)

        mark_cols_clean_out = 'mark_id,classification_id,subject_id,created_at,user_name,user_id,user_ip,tool,label,how_damaged,frame,x,y,lon_mark,lat_mark,lon_min,lon_max,lat_min,lat_max,imsize_x_pix,imsize_y_pix'.split(',')
        if not struc_subtask:
            mark_cols_clean_out.remove('how_damaged')

        marks_subj_clean[mark_cols_clean_out].to_csv(outfile_wsubj.replace(".csv", "-compact.csv"))

        print("%d marks matched to %d subjects; result output in %s." % (i_mark, len(subjects), outfile_wsubj))


    subj_cols_compact = 'lon_min lon_max lat_min lat_max imsize_x_pix imsize_y_pix'.split()

    ################################## matching blanks to subject info
    if i_empty > 0:
        theblanks = pd.read_csv(blankfile)
        blanks_subj = pd.merge(theblanks, subjects, how='left', on='subject_id', suffixes=('', '_2'))
        blank_cols_out = (theblanks.columns.values).tolist()
        all_cols_out = blank_cols_out + subj_cols_compact
        blankfile_wsubj = "%s/%s%s" % (outdir, freetext, blankfile_nodir.replace(".csv", "-wsubjinfo.csv"))
        blanks_subj[all_cols_out][np.invert(np.isnan(blanks_subj.imsize_y_pix))].to_csv(blankfile_wsubj)
        print(" ... saved %s" % blankfile_wsubj)



    ################################## matching questions to subject info
    if i_question > 0:
        thequestions = pd.read_csv(questionfile)
        questions_subj = pd.merge(thequestions, subjects, how='left', on='subject_id', suffixes=('', '_2'))
        question_cols_out = (thequestions.columns.values).tolist()
        all_cols_out = question_cols_out + subj_cols_compact
        questionfile_wsubj = "%s/%s%s" % (outdir, freetext, questionfile_nodir.replace(".csv", "-wsubjinfo.csv"))
        questions_subj[all_cols_out][np.invert(np.isnan(questions_subj.imsize_y_pix))].to_csv(questionfile_wsubj)
        print(" ... saved %s" % questionfile_wsubj)



    ################################## matching shortcuts to subject info
    if i_shortcut > 0:
        theshortcuts = pd.read_csv(shortcutfile)
        shortcuts_subj = pd.merge(theshortcuts, subjects, how='left', on='subject_id', suffixes=('', '_2'))
        shortcut_cols_out = (theshortcuts.columns.values).tolist()
        all_cols_out = shortcut_cols_out + subj_cols_compact
        shortcutfile_wsubj = "%s/%s%s" % (outdir, freetext, shortcutfile_nodir.replace(".csv", "-wsubjinfo.csv"))
        shortcuts_subj[all_cols_out][np.invert(np.isnan(shortcuts_subj.imsize_y_pix))].to_csv(shortcutfile_wsubj)
        print(" ... saved %s" % shortcutfile_wsubj)


else:
    print("OOPS: after filtering by subject set and workflow, you don't have any subjects to match to!")




if i_exception > 0:
    print("WARNING: There were %d exceptions (mark classification not formatted as expected). They were in rows:\n" % i_exception)
    print(exception_rows)


#end
