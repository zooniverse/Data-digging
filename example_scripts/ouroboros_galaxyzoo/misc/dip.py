from pymongo import MongoClient
from matplotlib import pyplot as plt
import numpy as np
from collections import Counter
import json
import os
import re
import datetime
import dateutil.parser
import pandas as pd
from gz_class import plurality
import itertools

"""

dip
=========

Generate progress reports and plots for the various subject sets in Galaxy Zoo (v4).

Kyle Willett (UMN) - 09 Dec 2015

"""

# Get data

gzdir = '/Users/willettk/Astronomy/Research/GalaxyZoo'
today = datetime.datetime.today()

client = MongoClient('localhost', 27017)

# Ouroboros project database
dbp = client['galaxy_zoo'] 

subjects = dbp['galaxy_zoo_subjects']
classifications = dbp['galaxy_zoo_classifications']
groups = dbp['galaxy_zoo_groups']

# Ouroboros Talk database
dbo = client['ouroboros']

subject_sets = dbo['subject_sets']
projects = dbo['projects']
discussions = dbo['discussions']

def survey_dict():

    # Information about the specific group settings in the project

    d = {u'candels':        {'name':u'CANDELS','retire_limit':80},
        u'candels_2epoch':  {'name':u'CANDELS 2-epoch','retire_limit':80},
        u'decals':          {'name':u'DECaLS','retire_limit':40},
        u'ferengi':         {'name':u'FERENGI','retire_limit':40},
        u'goods_full':      {'name':u'GOODS full-depth','retire_limit':40},
        u'illustris':       {'name':u'Illustris','retire_limit':40},
        u'sloan_singleband':{'name':u'SDSS single-band','retire_limit':40},
        u'ukidss':          {'name':u'UKIDSS','retire_limit':40}}
        #u'gzh':             {'name':u'Galaxy Zoo Hubble','retire_limit':48},
        #u'sloan':           {'name':u'SDSS DR8','retire_limit':60},        # Memory error - can't collate the full classification file in pandas

    return d
    
def expand_dict(d):

    # Turn a set of Counter values into a full list

    dl = []
    for x in d:
        dl.extend([int(x)]*d[x])

    return dl

def print_lc(last_classification,survey):

    # Print the classification dates to the log file

    day_interval = (today - last_classification).days
    suffix = 's' if day_interval != 1 else ''
    logline(survey,"\n\tThe most recent classification in the database was {0:.0f} day{1:} ago.".format(day_interval,suffix))

    return None
    
def most_recent(survey,ndays=14,log_date=True):

    # Find the date of the most recent classification

    workflow_id = get_workflow_id(survey)
    json_most_recent = "{0:}/progress/{1:}/most_recent.json".format(gzdir,survey)

    if os.path.exists(json_most_recent):
        with open(json_most_recent,'rb') as f:
            jmr = json.load(f)

        # Check if there are classifications between the last time code was run and today
        last_classification = dateutil.parser.parse(jmr['last_classification'])
        last_run = dateutil.parser.parse(jmr['last_run'])
        really_recent = classifications.find({'created_at':{'$gte':last_run},'workflow_id':workflow_id})
        if really_recent.count() == 0:
            # File exists and there are no new classifications since it was last run.
            if log_date:
                print_lc(last_classification,survey)
            # Update the field for last time it was run
            jmr['last_run'] = today.isoformat() 
            return last_classification

    # If stored data doesn't exist or needs updating, query the database. 
    # First try to see if there's data within the last two weeks; if not found, search the entire database.
    # Can be super slow - try building an index on "created_at" field first
    #
    recents = classifications.find({'created_at':{'$gte':today - datetime.timedelta(days=ndays)},'workflow_id':workflow_id})
    rc = recents.count()
    if rc == 0:
        recents = classifications.find({'workflow_id':workflow_id})

    # Sort by date created
    mrc = recents.sort([("created_at", -1)]).limit(1)
    last_classification = mrc.next()['created_at']

    if log_date:
        print_lc(last_classification,survey)

    # Save results to a file so we don't have to repeat database query unnecessarily

    jmr = {"last_run":today.isoformat(),"last_classification":last_classification.isoformat()}
    with open(json_most_recent,'wb') as f:
        json.dump(jmr,f)

    return last_classification

def check_paths(survey):

    # Create directories for writing plots, JSON, and txt files if they don't exist
    
    progress_path = '{0:}/progress/{1:}'.format(gzdir,survey)
    if not os.path.exists(progress_path):
        os.mkdir(progress_path)
        print "Creating sub-directory for {0:}".format(survey)

    return None

def get_workflow_id(survey):

    # Get the Mongo ObjectId for the workflow

    exsub = subjects.find_one({'metadata.survey':survey})

    return exsub['workflow_ids'][0]

def get_project_id(name='galaxy_zoo'):

    # Get the Mongo ObjectId for the project

    project = projects.find_one({'name':name}) 

    return project['_id']

def logline(survey,str_,mode='a',suppress=False):

    # Write a string describing the progress to a text file

    with open("{0:}/progress/{1:}/progress_{1:}.txt".format(gzdir,survey),'{0:}b'.format(mode)) as lf:

        print >> lf,str_
        if mode == 'a' and suppress == False:
            print(str_)

    return None
    
def good_subjects(survey):

    # Remove the DECaLS subjects erroneously uploded to Ouroboros. They're listed as complete, but with zero classifications.

    if survey == 'decals':
        goodsubs = {"metadata.survey":survey,"$or":[{'state':'complete','classification_count':{'$gt':0}},{'state':'active'}]}
    else:
        goodsubs = {"metadata.survey":survey,"state":{"$in":['active','complete']}}

    return goodsubs

def count_classifications(survey):

    # Write a summary of the output to a text file

    sd = survey_dict()[survey]
    survey_name = sd['name']
    retire_limit = sd['retire_limit']

    goodsubs = good_subjects(survey)
    
    subs = subjects.find(goodsubs)
    workflow_id = get_workflow_id(survey)

    logline(survey,'\n{0:} images'.format(survey_name))

    aggstate = subjects.aggregate([{"$match":goodsubs},{"$group":{"_id":"$state","count":{"$sum":1}}}])
    if aggstate['ok']:
        state_counts = {}
        for k in aggstate['result']:
            state_counts[k['_id']] = k['count']
        
    totalcounts = sum(state_counts.values())
    for k in state_counts:
        logline(survey,"\t{0:10} = {1:6.0f}".format(k,state_counts[k]))

    nc = 0
    for s in subs:
        nc += s['classification_count']
    logline(survey,"\n\t{0:} total classifications".format(nc))
    if aggstate['ok']:
        logline(survey,"\tAverage of {0:.1f} classifications per active subject".format(nc * 1./totalcounts))

    # Aggregate classifications by subject ID

    jsonfile = '{0:}/progress/{1:}/classifications_{1:}.json'.format(gzdir,survey)
    if not os.path.exists(jsonfile):

        print "Aggregating"
        aggsurvey = dbp[survey]
        aggsurvey.drop()

        agg = classifications.aggregate([{"$match":{"workflow_id":workflow_id}},
                                         {'$unwind':'$subject_ids'},
                                         {"$group":{"_id":"$subject_ids","count":{"$sum":1}}},
                                         {"$out":survey}])

        aggsurvey = dbp[survey]
        counts = [x['count'] for x in aggsurvey.find()]

        d = dict(Counter(counts))
        with open(jsonfile,'wb') as fp:
            json.dump(d,fp)

    else:

        with open(jsonfile,'rb') as fp:
            d = json.load(fp)

    counts = expand_dict(d)

    mrd = most_recent(survey)

    # Add the galaxies without any classifications for Method 1

    at_least_one = 0
    for k in d:
        at_least_one += d[k]
    counts.extend([0]*(subs.count()-at_least_one))
    counts2 = [x['classification_count'] for x in subjects.find(goodsubs)]
    
    # Plot the number of classifications done so far

    fig = plt.figure(figsize=(12,6))

    ax1 = fig.add_subplot(121)
    ax1.hist(counts,bins=np.arange(retire_limit+5))
    ax1.set_xlabel('Number of classifications per subject',fontsize=15)
    ax1.set_ylabel('Count',fontsize=15)
    ax1.set_title('{0:} - aggregating classifications'.format(survey_name))

    #print "Method 1: {0:.0f} classifications".format(np.sum(counts))

    # Try with classifications

    ax2 = fig.add_subplot(122)
    h,bin_edges,patches = ax2.hist(counts2,bins=np.arange(retire_limit+5))
    ax2.set_xlabel('Number of classifications per subject',fontsize=15)
    ax2.set_ylabel('Count',fontsize=15)
    ax2.set_title('Classification counts as of {0:}'.format(mrd.strftime("%d %b %Y")))

    #print "Method 2: {0:.0f} classifications".format(np.sum(counts2))

    ax1.set_ylim(0,max([ax1.get_ylim()[1],ax2.get_ylim()[1]]))
    ax2.set_ylim(0,max([ax1.get_ylim()[1],ax2.get_ylim()[1]]))

    fig.set_tight_layout(True)

    # Print the number of retired subjects on the plot

    n_retired = np.sum(h[bin_edges[:-1] >= retire_limit])
    logline(survey,"\n\t{0:.0f} subjects are retired (with at least {1:.0f} classifications).".format(n_retired,retire_limit))

    ax2.text(2,ax2.get_ylim()[1]*0.90,r"$N_{finished}=$"+"{0:.0f}".format(n_retired),fontsize=14)

    fig.set_tight_layout(True)
    plt.savefig('{0:}/progress/{1:}/classifications_{1:}.png'.format(gzdir,survey))
    plt.close()

    return counts2

def finish_date(survey,counts):

    # When are the datasets projected to be done?

    workflow_id = get_workflow_id(survey)
    sd = survey_dict()[survey]
    survey_name = sd['name']
    retire_limit = sd['retire_limit']

    mrd = most_recent(survey,log_date=False)

    avg_period = 30
    avg_perday = classifications.find({"created_at":{"$lt":mrd,"$gte":mrd-datetime.timedelta(days=avg_period)}, "workflow_id":workflow_id}).count() * 1./avg_period

    c = Counter(counts)
    remaining_classifications = 0
    for x in c:
        if x < retire_limit:
            remaining_classifications += c[x] * (retire_limit-x)
    remaining_time = remaining_classifications * 1./avg_perday

    finish_date = mrd + datetime.timedelta(days=int(remaining_time))
    days_left = (finish_date - today).days

    # But I want the time elapsed since the last recorded classification, not today!

    # Double-check to see if there are active subjects

    active_counts = True if subjects.find({'metadata.survey':survey,'state':'active'}).count() > 0 else False

    suffix = 's' if abs(days_left) != 1 else ''
    if active_counts and remaining_classifications > 0:
        logline(survey,"\n\tCurrent rate of classifications for {0:} workflow is {1:.0f}/day.".format(survey_name,avg_perday))
        logline(survey,"\n\t{0:} active subjects will be completed in {1:.0f} day{3:} ({2:}) at current rate.".format(survey_name,days_left,finish_date.strftime("%d %b %Y"),suffix))
    else:
        logline(survey,"\n\tNo active subjects remaining for {0}.".format(survey_name))

    return None

def get_tags(zooniverse_id,_format='str'):

    # Get the Talk tags for a particular object

    focused_discussions = discussions.find({'focus._id':zooniverse_id})
    taglist = []
    for fd in focused_discussions:
        for comment in fd['comments']:
            taglist.append(comment['tags'])
    if _format == 'list':
        return taglist
    else:

        tags_str = ', '.join([item for sublist in taglist for item in sublist])

        if len(tags_str) == 0:
            tags_str = None

        return tags_str

def most_collected(survey):

    # What are the most collected subjects for the project?

    n_collected = 10
    
    gzcollections = subject_sets.find({'project_id':get_project_id()})
    gzcs = []
    for gzc in gzcollections:
        if gzc.has_key('subjects'):
            gzcs.extend([x['zooniverse_id'] for x in gzc['subjects']])

    # Only select subjects for this particular survey/workflow
    goodsubs = good_subjects(survey)
    zids = [x['zooniverse_id'] for x in subjects.find(goodsubs)]
    cc_all = Counter(gzcs)
    set_cc = set(cc_all.keys())
    set_zids = set(zids)

    cc_project = Counter()
    for s in set_cc.intersection(set_zids):
        cc_project[s] = cc_all[s]

    sd = survey_dict()[survey]
    survey_name = sd['name']

    commonly_collected = cc_project.most_common(n_collected)
    logline(survey,"\n\tMost commonly collected {0:} images in Talk:\t#tags".format(survey_name))
    logline(survey,"\t{0:}".format('-'*75),suppress=True)

    for m in commonly_collected:
        tags_cc = get_tags(m[0])
        logline(survey,"\t\t{0:} is in {1:3.0f} collections\t\t\t\t{2:}".format(m[0],m[1],tags_cc))

    # Plot histogram

    cvals = cc_project.values()
    cvals.extend([0]*(len(zids) - len(cc_project)))

    fig = plt.figure(figsize=(6,6))
    ax = fig.add_subplot(111)
    ax.hist(cvals,bins=np.arange(max(cvals)+2))
    ax.set_yscale('log')
    ax.set_xlabel('Subjects in '+r'$N$'+' collections',fontsize=15)
    ax.set_ylabel(r'$N$',fontsize=15)
    ax.set_title('{0:} subjects in Talk collections'.format(survey_name))

    fig.set_tight_layout(True)
    plt.savefig('{0:}/progress/{1:}/collections_{1:}.png'.format(gzdir,survey))
    plt.close()

    return None

def most_discussed(survey):

    # What are the most discussed subjects for the project?

    n_discussed = 10
    
    gzdiscussions = discussions.find({'project_id':get_project_id(),'focus.base_type':'Subject'})
    gzds = [gzd['focus']['_id'] for gzd in gzdiscussions]

    # Only select subjects for this particular survey/workflow
    dc_all = Counter(gzds)
    set_dc = set(dc_all.keys())

    goodsubs = good_subjects(survey)
    zids = [x['zooniverse_id'] for x in subjects.find(goodsubs)]
    set_zids = set(zids)

    dc_project = Counter()
    for s in set_dc.intersection(set_zids):
        dc_project[s] = dc_all[s]

    commonly_discussed = dc_project.most_common(n_discussed)

    sd = survey_dict()[survey]
    survey_name = sd['name']

    logline(survey,"\n\tMost commonly discussed {0:} images in Talk:\t#tags".format(survey_name))
    logline(survey,"\t{0:}".format('-'*75),suppress=True)

    for m in commonly_discussed:
        tags_cd = get_tags(m[0])
        logline(survey,"\t\t{0:} is in {1:3.0f} discussions\t\t\t\t{2:}".format(m[0],m[1],tags_cd))
    
    # Plot histogram

    dvals = dc_project.values()
    dvals.extend([0]*(len(zids) - len(dc_project)))

    fig = plt.figure(figsize=(6,6))
    ax = fig.add_subplot(111)
    ax.hist(dvals,bins=np.arange(max(dvals)+2))
    ax.set_yscale('log')
    ax.set_xlabel('Subjects discussed '+r'$N$'+' times',fontsize=15)
    ax.set_ylabel(r'$N$',fontsize=15)
    ax.set_title('Talk discussions centered on {0:} subjects'.format(survey_name))

    fig.set_tight_layout(True)
    plt.savefig('{0:}/progress/{1:}/discussions_{1:}.png'.format(gzdir,survey))
    plt.close()

    return None

def most_common_tags(survey,n=10):

    # What are the most common hashtags in this project?
    #
    decals_galaxies = subjects.find({'metadata.survey':'decals'})

    taglist = []
    for gal in decals_galaxies:
        nested_list = get_tags(gal['zooniverse_id'],_format='list')
        chain = itertools.chain(*nested_list)
        taglist.extend(list(chain))

    c = Counter(taglist)

    return c

def is_number(s):

    # Is a string a representation of a number?

    try:
        int(s)
        return True
    except ValueError:
        return False

def morphology_distribution(survey,absolute_counts=False):

    # What's the distribution of morphologies so far?

    """
        Get the updated version of Brooke's aggregation and weighting code
        Try running it on the DECaLS and Illustris data
        Assuming it works, match positionally against GZ2 in TOPCAT (both samples). This might have to be manual
            unless I find a faster implementation of positional matching in Python.
       Adapt the GZ2 code for plurality classifications and run on GZ4 data
       Summarize overall results and split by luminosity
       List galaxies with large changes?
    """

    # Get weights
    try:
        collation_file = "{0:}/gz_reduction_sandbox/data/{1:}_unweighted_classifications_00.csv".format(gzdir,survey)
        collated = pd.read_csv(collation_file)
    except IOError:
        print "Collation file for {0:} does not exist. Aborting.".format(survey)
        return None

    columns = collated.columns

    fraccols,colnames = [],[]
    for c in columns:
        if c[-4:] == 'frac':
            fraccols.append(c)
        if c[0] == 't' and is_number(c[1:3]):
            colnames.append(c[:3])

    collist = list(set(colnames))
    collist.sort()

    # Plot distribution of vote fractions for each task

    ntasks = len(collist)
    ncols = 4 if ntasks > 9 else int(np.sqrt(ntasks))
    nrows = int(ntasks / ncols) if ntasks % ncols == 0 else int(ntasks / ncols) + 1

    sd = survey_dict()[survey]
    survey_name = sd['name']

    def f7(seq):
        seen = set()
        seen_add = seen.add
        return [x for x in seq if not (x in seen or seen_add(x))] 

    tasklabels = f7([re.split("[ax][0-9]",f)[0][4:-1] for f in fraccols])
    labels = [re.split("[ax][0-9]",f[4:-5])[-1][1:] for f in fraccols]

    fig,axarr = plt.subplots(nrows=nrows,ncols=ncols,figsize=(15,12))

    for i,c in enumerate(collist):
        ax = axarr.ravel()[i]
        title = '{0:} - t{1:02} {2:}'.format(survey_name,i,tasklabels[i]) if i == 0 else 't{0:02} {1:}'.format(i,tasklabels[i])
        ax.set_title(title)
        for f in fraccols:
            if f[:3] == c and f[-15:-5] != 'a0_discuss':
                label = re.split("[ax][0-9]",f[4:-5])[-1][1:]
                ax.hist(collated[f],alpha=0.7,label=label)
        ax.set_xlim(0,1)
        ax.legend(loc='upper left',fontsize=6)

    # Remove empty axes from subplots
    if axarr.size > ntasks:
        for i in range(axarr.size - ntasks):
            ax = axarr.ravel()[axarr.size-(i+1)]
            ax.set_axis_off()

    fig.set_tight_layout(True)
    plt.savefig('{0:}/progress/{1:}/votefractions_{1:}.png'.format(gzdir,survey))

    # Make pie charts of the plurality votes

    votearr = np.array(collated[fraccols])
    class_arr,task_arr,task_ans = [],[],[]
    for v in votearr:
        e,a = plurality(v,survey) 
        task_arr.append(e)
        task_ans.append(a)

    task_arr = np.array(task_arr)
    task_ans = np.array(task_ans)

    fig,axarr = plt.subplots(nrows=nrows,ncols=ncols,figsize=(15,12))

    colors=[u'#377EB8', u'#E41A1C', u'#4DAF4A', u'#984EA3', u'#FF7F00',u'#A6761D',u'#1B9E77']

    n = (task_arr.shape)[1]
    for i in range(n):
        ax = axarr.ravel()[i]
        c = Counter(task_ans[:,i][task_arr[:,i] == True])
        pv,pl = [],[]
        for k in c:
            pv.append(c[k])
            pl.append(labels[k])
        if absolute_counts:
            ax.pie(pv,labels=pl,colors=colors,autopct=lambda(p): '{:.0f}'.format(p * sum(pv) / 100))
        else:
            ax.pie(pv,labels=pl,colors=colors,autopct='%1.0f%%')
        title = '{0:} - t{1:02} {2:}'.format(survey_name,i,tasklabels[i]) if i == 0 else 't{0:02} {1:}'.format(i,tasklabels[i])
        ax.set_title(title)
        ax.set_aspect('equal')

    # Remove empty axes from subplots
    if axarr.size > ntasks:
        for i in range(axarr.size - ntasks):
            ax = axarr.ravel()[axarr.size-(i+1)]
            ax.set_axis_off()

    fig.set_tight_layout(True)
    plt.savefig('{0:}/progress/{1:}/pie_{1:}.png'.format(gzdir,survey))
    plt.close()

    # How does the distribution compare to GZ1 and GZ2?


    # Have they discovered anything interesting? 

    """
        Look at long discussions? Maybe tag the ones that science team hasn't participated in yet?
    """

    return None

if __name__ == "__main__":

    do_all = True
    surveys = survey_dict().keys() if do_all else ('decals',)

    for survey in surveys:

        # Create directory paths if necessary
        check_paths(survey)

        # Open the logfile
        logline(survey,"Progress report as of {0:}".format(today.strftime("%d %b %Y")),mode='w')
        
        # Run progress updates
        counts = count_classifications(survey)
        finish_date(survey,counts)
        most_collected(survey)
        most_discussed(survey)
        morphology_distribution(survey)

    # Ideas: get the images for the most-discussed/collected images. What are their tags? Why are people discussing/collecting them?

