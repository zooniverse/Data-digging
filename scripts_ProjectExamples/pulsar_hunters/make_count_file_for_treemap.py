import sys, os
import random
import pandas as pd
import json

# the full classification file has >3M rows, which takes a long time to process,
# and also GitHub doesn't like it very much so we're not adding it to the repo
classfile_in  = 'pulsar-hunters-classifications_first500k.csv'
#classfile_in  = '9e6c81af-3688-48b9-aa13-61a612e9b32b.csv'
countfile_out = 'class_counts_colors.csv'

# this does a classification count for each user and assigns each user a random
# HTML color code (greyscale if the user is anonymous, RGB if not)
# The output file generated here can be used as an input to treemap.R
# note that while generating this file is quick, the treemap will take a looong time
# (Took me >24 hours once when running it for all users on a big project)

# assign a color randomly if logged in, gray otherwise
def randcolor(user_label):
    if user_label.startswith('not-logged-in-'):
        # keep it confined to grays, i.e. R=G=B and not too bright, not too dark
        g = random.randint(25,150)
        return '#%02X%02X%02X' % (g,g,g)
        #return '#555555'
    else:
        # the lambda makes this generate a new int every time it's called, so that
        # in general R != G != B below.
        r = lambda: random.randint(0,255)
        return '#%02X%02X%02X' % (r(),r(),r())





# Get the Gini coefficient - https://en.wikipedia.org/wiki/Gini_coefficient
# Typical values of the Gini for healthy Zooniverse projects (Cox et al. 2015) are
#  in the range of 0.7-0.9.

def gini(list_of_values):
    sorted_list = sorted(list_of_values)
    height, area = 0, 0
    for value in sorted_list:
        height += value
        area += height - value / 2.
    fair_area = height * len(list_of_values) / 2
    return (fair_area - area) / fair_area





def get_alternate_sessioninfo(row):

    if not row[1]['user_name'].startswith('not-logged-in'):
        return row[1]['user_name']
    else:
        metadata = row[1]['meta_json']
        # session, if it exists
        # (ip, agent, viewport_width, viewport_height) if session doesn't exist
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




print("Reading classifications from %s ..." % classfile_in)

classifications = pd.read_csv(classfile_in)


# first, extract the started_at and finished_at from the annotations column
classifications['meta_json'] = [json.loads(q) for q in classifications.metadata]

# we need to set up a new user id column that's login name if the classification is while logged in,
# session if not (right now "user_name" is login name or hashed IP and, well, read on...)
# in this particular run of this particular project, session is a better tracer of uniqueness than IP
# for anonymous users, because of a bug with some back-end stuff that someone else is fixing
# but we also want to keep the user name if it exists, so let's use this function
#classifications['user_label'] = [get_alternate_sessioninfo(q) for q in classifications.iterrows()]
classifications['user_label'] = [get_alternate_sessioninfo(q) for q in classifications['user_name meta_json'.split()].iterrows()]

classifications['count'] = [1 for q in classifications.workflow_version]

by_user = classifications.groupby('user_label')
class_counts = pd.DataFrame(by_user['count'].aggregate('sum'))
class_counts['color'] = [randcolor(q) for q in class_counts.index]
class_counts.sort_values(['count'], ascending=False, inplace=True)
class_counts.to_csv(countfile_out)

print("Gini coefficient for project: %.3f\nCounts printed to %s\n" % (gini(class_counts['count']), countfile_out))
