from pymongo import MongoClient 
import datetime
import os,sys
import json
from collections import Counter
from matplotlib import pyplot as plt
import pandas as pd
import numpy as np
import seaborn as sns

# Plot the activity of both users and the science team for a Zooniverse project (on Ouroboros) 
#
# eg:
# > python ouroboros_talk_stats.py galaxy_zoo
#
# Requires:
#
#       - project data restored into a local MongoDB
#       - Talk data from ouroboros restored into a local MongoDB

try:
    project_name = sys.argv[1]
except IndexError:
    print "\nExpected arguments: "
    print "\t> python ouroboros_talk_stats.py project_name [save_path]"
    print "\nExamples:"
    print "\t> python ouroboros_talk_stats.py galaxy_zoo"
    print "\t> python ouroboros_talk_stats.py galaxy_zoo ~/Astronomy/Research/GalaxyZoo/"
    sys.exit(0)

try:
    path = sys.argv[2]
    if not os.path.exists(path):
        print "Cannot find {0:}".format(path)
        sys.exit(0)
except IndexError:
    defaultpath = '/Users/willettk/Astronomy/Research/GalaxyZoo/'
    if os.path.exists(defaultpath):
        path = defaultpath
    else:
        path = './'

# Check paths

def check_paths(name,oldpath=path):
    newpath = "{0:}{1:}/".format(oldpath,name)
    if not os.path.exists(newpath):
        os.mkdir(newpath)
    return newpath

jsonpath = check_paths('json')
plotpath = check_paths('plots')

# Load Mongo data

client = MongoClient('localhost', 27017)
db = client['ouroboros'] 

boards = db['boards']
discussions = db['discussions']
projects = db['projects']
subject_sets = db['subject_sets']
users = db['users']

project = projects.find_one({'name':project_name})
science_team = users.find({"talk.roles.{0:}".format(project['_id']):"scientist"})

print("\nThere are {0:} people on the {1:} science team".format(science_team.count(),project['display_name']))

# Count the number of interactions by the science team
times = []
person = []
for member in science_team:
    d = discussions.find({'user_ids':member['_id'],'project_id':project['_id']})
    count = d.count()
    if count > 0:
        for discussion in d:
            times.append(discussion['created_at'])
            person.append(member)
        print "Talk interactions on Galaxy Zoo involving {0:20}: {1:.0f}".format(member['name'],count)
    else:
        print "No discussions involving {0:}".format(member['name'])

# Since querying large databases takes time, save results to file the first time around.

class_file = '{0:}{1:}_aggregate_classifications.json'.format(jsonpath,project_name)
if not os.path.exists(class_file):

    # Aggregate the classification data
    
    db_class = client[project_name]
    classifications = db_class['{0:}_classifications'.format(project_name)]
    aggarr = classifications.aggregate({ '$group' : { '_id': { 'year' : { '$year' : "$created_at" }, 'month' : { '$month' : "$created_at" }, 'day' : { '$dayOfMonth' : "$created_at" }, }, 'count': { '$sum': 1 } }})
    aggclass = aggarr['result']
    # Save to file
    if len(aggclass) > 0:
        with open(class_file,'wb') as f:
            json.dump(aggclass,f)
    else:
        print "\nNo classification results found in Mongo for {0:} - exiting.\n".format(project_name)
        sys.exit(0)

else:
    # Read from file
    with open(class_file,'rb') as f:
        aggclass = json.load(f)

discussion_file = '{0:}{1:}_discussions_all.json'.format(jsonpath,project_name)
if not os.path.exists(discussion_file):

    # Aggregate the Talk data
    
    aggarr = discussions.aggregate([{'$match':{'project_id':project['_id']}}, {'$group' : { '_id': { 'year' : { '$year' : "$created_at" }, 'month' : { '$month' : "$created_at" }, 'day' : { '$dayOfMonth' : "$created_at" }, }, 'count': { '$sum': 1 } }}])
    aggtalk = aggarr['result']
    if len(aggtalk) > 0:
        with open(discussion_file,'wb') as f:
            json.dump(aggtalk,f)
    else:
        print "\nNo Talk results found in Mongo for {0:} - exiting.\n".format(project_name)
        sys.exit(0)
else:
    # Read from file
    with open(discussion_file,'rb') as f:
        aggtalk = json.load(f)

    
def parse_counts(d):

    cd = [(datetime.date(x['_id']['year'],x['_id']['month'],x['_id']['day']),x['count']) for x in d]
    class_data = sorted(cd, key=lambda x: x[0])
    d = [x[0] for x in class_data]
    c = [x[1] for x in class_data]

    return d,c

dates_classifications,counts_classifications = parse_counts(aggclass)
dates_alltalk,counts_alltalk = parse_counts(aggtalk)

dates_science = [d.date() for d in times]
c = Counter(dates_science)

posts_scienceteam = []
for date in dates_classifications:
    if c.has_key(date):
        posts_scienceteam.append(c[date])
    else:
        posts_scienceteam.append(0)

# Put all the data in a single DataFrame

d = {'classifications':pd.Series(counts_classifications,index=dates_classifications),
    'all_posts':pd.Series(counts_alltalk,index=dates_alltalk),
    'science_team_posts':pd.Series(posts_scienceteam,index=dates_classifications)}

df = pd.DataFrame(d)

# Re-order the columns
cols = ['classifications','all_posts','science_team_posts']
df = df[cols]

# Plot #1: plot classifications, science team posts, and all user posts as a function of time

plt.rcParams['figure.figsize'] = 11, 7

main = plt.subplot2grid((4,4), (0, 0), rowspan=3, colspan=4)
main.plot(df.index, df['science_team_posts'], label='Science team')
main.plot(df.index, df['all_posts'], label='All posts')
main.axes.xaxis.set_ticklabels([])
main.axes.xaxis.set_label('Count')
main.axes.set_ylim([0,500])

plt.title('Posts on Talk')
plt.legend()

clss = plt.subplot2grid((4,4), (3,0), rowspan=1, colspan=4)
clss.bar(df.index, df['classifications'])

plt.title('Daily Classifications')

plotfile1 = "{0:}talk_{1:}_timeseries.png".format(plotpath,project_name)
plt.savefig(plotfile1)
print "\nPlot 1 saved as {0:}".format(plotfile1)

# Plot #2: combine the science team and user classifications into a single sub-plot

window_size = 3
pd.rolling_median(df[10:],window_size).plot(subplots=True,title='{0:} data smoothed over {1:.0f}-day window'.format(project['display_name'],window_size))

plotfile2 = "{0:}talk_{1:}_summary.png".format(plotpath,project_name)
plt.savefig(plotfile2)
print "Plot 2 saved as {0:}".format(plotfile2)
