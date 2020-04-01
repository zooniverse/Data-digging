import sys, os
import numpy as np
import pandas as pd
import json

#from get_workflow_info import get_workflow_info

project_name = "flying-hi"

infile        = "%s-classifications.csv" % project_name
#workflow_file = "%s-workflows.csv"       % project_name


workflow_id = 3590
workflow_version = 12.33

# the order of tools is from the workflow information - as is the fact there's
# only 1 task, T0
tools = ['galaxy', 'fiber', 'other']


# okay turns out we didn't really need this but I'm hoping it will make it easier to generalize later
#workflow_df = pd.read_csv(workflow_file)
#workflow_info = get_workflow_info(workflow_df, workflow_id, int(workflow_version))


classifications_all = pd.read_csv(infile)

classifications_all['anno_json'] = [json.loads(q) for q in classifications_all['annotations']]

# only use classifications from the workflow & version we care about
in_workflow = classifications_all.workflow_version == workflow_version

classifications = classifications_all[in_workflow]


'''
Rather than try to somehow save different marks to the same file without that
file becoming unmanageable, I'm going to create separate output files for each
type of mark.

Also, I noticed during a previous project that pandas (I think it was pandas
and not some more fundamental property of python itself?) seemed *very*
slow when trying to build a large dataframe or series of marks and then write
the whole thing to a file in one go. For a project with lots of classifications
it will be much faster to write line-by-line to a csv file and then, if needed,
read in the csv file at the end of the loop through the classifications.

'''


fgal = open("%s-marks-galaxy.csv" % project_name, "w")
ffib = open("%s-marks-fiber.csv"  % project_name, "w")
foth = open("%s-marks-other.csv"  % project_name, "w")
# this will keep track of classifications where the user said there was nothing there
# these may be important for some user weighting schemes etc.
femp = open("%s-marks-blank.csv"  % project_name, "w")

# write the header line for each of the files
# each has the basic classification information + the mark information
# including sanity check stuff + stuff we may never need, like the tool number
# and the frame the user drew the mark on, respectively

# the galaxy marker is a point: {(x, y)}
fgal.write("mark_id,classification_id,subject_id,created_at,user_name,user_id,user_ip,tool,frame,x,y\n")

# the fiber marker is a line: {(x1, y1), (x2, y2)}
ffib.write("mark_id,classification_id,subject_id,created_at,user_name,user_id,user_ip,tool,frame,x1,y1,x2,y2\n")

# the other/interesting marker is an ellipse+tag: {(x, y), (rx, ry), angle, text}
foth.write("mark_id,classification_id,subject_id,created_at,user_name,user_id,user_ip,tool,frame,x,y,rx,ry,angle,text\n")

# the blank table just needs the classification information
femp.write("classification_id,subject_id,created_at,user_name,user_id,user_ip\n")


# now extract the marks from each classification
# people who say Python should never need for loops are either way better at it
# than I am or have never dealt with Zooniverse classification exports
# (or both)
i_empty = 0
i_mark = 0
for i, row in enumerate(classifications.iterrows()):
    # row[0] is the index, [1] is the classification info
    cl = row[1]

    class_id   = cl['classification_id']
    subject_id = cl['subject_ids']
    created_at = cl['created_at']
    username   = cl['user_name']
    userid     = cl['user_id']
    userip     = cl['user_ip']

    # for anonymous users the userid field is blank so reads as NaN
    # which will throw an error later
    if np.isnan(userid):
        userid = -1

    # loop through annotations in this classification
    # (of which there can be arbitrarily many)
    for j, anno in enumerate(cl['anno_json']):
        # not sure we actually need these right now as there's only 1 task
        #thetask  = anno['task']
        #thelabel = anno['task_label']

        # first, if this classification is blank, just write the basic information
        if len(anno['value']) < 1:
            i_empty+=1
            femp.write("%d,%d,\"%s\",\"%s\",%d,%s\n" % (class_id, subject_id, created_at, username, userid, userip))
        else:
            # it's not empty, so let's collect other info
            # the marks themselves are in anno['value'], as a list
            for i_v, thevalue in enumerate(anno['value']):
                i_mark+=1

                # how we write to the file (and which file) depends on which tool
                # is being used
                #
                # the annotation json returns an integer that's the index of the
                # tools array we defined earlier
                # obviously I could just use the integer but this is easier to read
                # so worry about string vs int compare speeds when you have many
                # millions of classifications
                thetool = tools[thevalue['tool']]

                if thetool == "galaxy":
                    fgal.write("%d,%d,%d,\"%s\",\"%s\",%d,%s,%d,%d,%.2f,%.2f\n" % (i_mark, class_id, subject_id, created_at, username, userid, userip, thevalue['tool'], thevalue['frame'], thevalue['x'], thevalue['y']))

                elif thetool == "fiber":
                    ffib.write("%d,%d,%d,\"%s\",\"%s\",%d,%s,%d,%d,%.2f,%.2f,%.2f,%.2f\n" % (i_mark, class_id, subject_id, created_at, username, userid, userip, thevalue['tool'], thevalue['frame'], thevalue['x1'], thevalue['y1'], thevalue['x2'], thevalue['y2']))

                elif thetool == "other":
                    foth.write("%d,%d,%d,\"%s\",\"%s\",%d,%s,%d,%d,%.2f,%.2f,%.2f,%.2f,%.2f,\"%s\"\n" % (i_mark, class_id, subject_id, created_at, username, userid, userip, thevalue['tool'], thevalue['frame'], thevalue['x'], thevalue['y'], thevalue['rx'], thevalue['ry'], thevalue['angle'], thevalue['details'][0]['value'].replace("\n","").encode('utf-8')))



fgal.close()
ffib.close()
foth.close()
femp.close()


print("Saved %d marks from %d classifications (of which %d were empty) to %s-marks-*.csv." % (i_mark, len(classifications), i_empty, project_name))


#
