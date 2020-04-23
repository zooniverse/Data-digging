# um so I never ran this at the command line
# only ever used ipython (4.2.0) for it
# probably means I should make this a notebook
import sys, os
import numpy as np
import pandas as pd
#import matplotlib.pyplot as plt
import json
from datetime import datetime

'''

The aggregation code we've been using has some weird behaviors and might have
a bug. I didn't write that code and I can't easily track down the bug. It
may be required that we aggregate the bar lengths ourselves. I'd prefer not to,
but nevertheless I'm moving forward here.

The purpose of this code is to read in the raw classifications and extract
just the line drawing marks, then export them to a csv file with one row per
subject-line-drawing pair.

We collected line drawings in two workflows, with ids:
workflow_id == 3, workflow_version == 56.13
workflow_id == 1422, workflow_version == 10.8

so we'll only worry about those, but we'll treat them as the same here once we
extract them.

'''
#####################################
# define some stuff
#####################################

classfile_in = 'galaxy-zoo-bar-lengths-classifications.csv'
markfile_out = 'galaxy-zoo-bar-lengths-line-drawings.csv'

workflow_ids = [3, 1422]
workflow_int_versions = [56, 10]
# also the drawing task is the fourth task in workflow 3 and the initial task in workflow 1422
workflow_int_tasks = [3, 0]

# a function we will use later, extracting a particular task from a classification
# and failing gracefully if that task doesn't exist
def get_marks(q, i):
    try:
        return q[i]
    except:
        return '[]'

#####################################
# read the file
#####################################
# the memory parameter is because this is a big file and some of the columns take a bit more processing, so I'm telling pandas not to take a shortcut
classifications_all = pd.read_csv(classfile_in, low_memory=False)

#####################################
# do some work
#####################################
#
# break out some columns
#
# the subject_ids are currently stored oddly and this needs fixing
classifications_all['subject_id'] = [q.split(";")[0] for q in classifications_all.subject_ids]

# we only care about the major workflow version (e.g. "56" from 56.13)
# casting to integer doesn't round, it just cuts off the decimal, i.e. what we want
classifications_all['workflow_major'] = classifications_all.workflow_version.astype(int)

# make annotations (the actual classification content) something more readable - the current column is just a string but it's formatted to be read as a json/list
classifications_all['anno_json'] = [json.loads(q) for q in classifications_all.annotations]

# we are going to extract the line drawings from each workflow and then combine the 2 workflows together again

for i_w, wid in enumerate(workflow_ids):
    # get the line markings based on which task is right for this workflow_id
    classifications_all['lines'] = [get_marks(q, workflow_int_tasks[i_w]) for q in classifications_all.anno_json]

    # identify the rows where the classification is in the correct workflow & version
    relevant_classifications = (classifications_all.workflow_id == wid) & (classifications_all.workflow_major == workflow_int_versions[i_w])

    # I'm sure there's a better way to do this but this ... should... work for now
    # assuming .copy() actually works.
    if i_w == 0:
        first_class = classifications_all[relevant_classifications].copy()
    else:
        second_class = classifications_all[relevant_classifications].copy()


# now join the 2 subsets
both = [first_class, second_class]

both_class_all = pd.concat(both)

# now let's not worry about the classifications where no lines were drawn
# to identify which aren't empty we need to parse each row (loop) and also force the lines column value to be read as a string
has_marks = [len(q) > 3 for q in both_class_all.lines.astype(str)]

both_class = both_class_all[has_marks]

#In [117]: len(both_class)
#Out[117]: 65088

# Now we need to go through each row of this dataframe and break out individual line marks into separate rows. I don't see any way around this requiring a for loop.

# initialize the dict so we can add to it later
line_marks = 0
line_marks = pd.DataFrame()

# also we'll use this to track unique marking ids
mark_id = 0

# loop through each row in both_class
# this seems so very unpythonic
for i, row in enumerate(both_class.iterrows()):
    thelines = row[1].lines['value']
    # loop through each individual line marking
    for themark in thelines:
        line_mark_class = {}
        line_mark_class['mark_id'] = mark_id
        line_mark_class['classification_id'] = row[1]['classification_id']
        line_mark_class['subject_id'] = row[1]['subject_id']
        line_mark_class['user_name'] = row[1]['user_name']
        line_mark_class['user_id'] = row[1]['user_id']
        line_mark_class['user_ip'] = row[1]['user_ip']
        line_mark_class['created_at'] = row[1]['created_at']
        line_mark_class['workflow_id'] = row[1]['workflow_id']
        line_mark_class['workflow_version'] = row[1]['workflow_version']
        line_mark_class['x1'] = themark['x1']
        line_mark_class['y1'] = themark['y1']
        line_mark_class['x2'] = themark['x2']
        line_mark_class['y2'] = themark['y2']
        line_mark_class['i_tool'] = themark['tool']

        qq = pd.Series(line_mark_class)

        if len(line_marks) == 0:
            line_marks = pd.DataFrame(qq).T
        else:
            line_marks = pd.concat([line_marks, pd.DataFrame(qq).T])

        mark_id +=1

    if i % 10000 == 0:
        print("Mark %d recorded at %s ..." % (i, str(datetime.now())))

# Note: the above is VERY slow and each iteration takes longer the farther in the loop you are. I'd probably have better results manually writing each line to a csv file and then re-reading it in below.


line_marks.set_index('mark_id', inplace=True)

# compute the slope and intercepts of each line
# m = (y2-y1)/(x2-x1) with some stuff to make sure we're not dividing by integers
line_marks['slope'] = (line_marks.y2.astype(float) - line_marks.y1.astype(float)) / (line_marks.x2.astype(float) - line_marks.x1.astype(float))
# b = y1 - m*x1
line_marks['intercept'] = line_marks.y1.astype(float) - (line_marks.slope * line_marks.x1.astype(float))

# compute the length of each line - this is just the pythagorean theorem
dist_x = line_marks.x1.astype(float) - line_marks.x2.astype(float)
dist_y = line_marks.y1.astype(float) - line_marks.y2.astype(float)
len2 = (dist_x*dist_x) + (dist_y*dist_y)
line_marks['length'] = [np.sqrt(q) for q in len2]

# this sets not just which columns are printed but also the order they're printed in
# note the mark_id column was set as the index so will be printed as column 1 and doesn't need an extra mention here
columns_toprint = 'classification_id subject_id user_name user_id user_ip created_at workflow_id workflow_version x1 x2 y1 y2 slope intercept length i_tool'.split()
line_marks[columns_toprint].to_csv(markfile_out)


# # I paste stuff like this into ipython to help me figure out the structure of the beast
# # this is how I knew that all the important stuff in each row is in row[1],
# # how I knew that the important stuff in the "lines" column was then under ['value']
# # etc.
# #
# # Note you have to type %paste into ipython instead of actually pasting, because otherwise the line indents don't get read properly
# for i, row in enumerate(both_class.iterrows()):
#     print(i)
#     print(row)
#     print(row[1].lines)
#     print("Marcooooooo")
#     markings = row[1].lines["value"]
#     for themark in markings:
#         print(themark)
#         print("holla")
#     print("Poloooooooo")
#     if (i > 3):
#         break







#end
