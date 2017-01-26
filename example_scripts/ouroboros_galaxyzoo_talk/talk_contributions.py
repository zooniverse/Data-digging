from pymongo import MongoClient
from matplotlib import pyplot as plt
import numpy as np
from collections import Counter

# How many people classifying on a project contributed to Talk?

project_name = 'radio'

# Get data

def load_data():

    client = MongoClient('localhost', 27017)
    
    # Ouroboros project database
    dbp = client[project_name] 
    classifications = dbp['{0}_classifications'.format(project_name)]
    
    # Ouroboros Talk database
    dbo = client['ouroboros']
    projects = dbo['projects']
    discussions = dbo['discussions']

    return classifications,projects,discussions

def get_project_id(projects):

    # Get the Mongo ObjectId for the project

    project = projects.find_one({'name':project_name}) 

    return project['_id']

def get_talkers(projects,discussions):

    # How many participants in Talk have there been?
    
    project_id = get_project_id(projects)

    project_discussions = discussions.find({'project_id':project_id})
    talker_list = []
    
    for rd in project_discussions:
        talker_list.extend(rd['user_ids'])
    
    return talker_list

def get_classifiers(classifications):
    
    # How many total classifiers have there been?
    
    registered_classifications = classifications.find({'user_id':{'$exists':'true'}})
    classifier_list = [rc['user_id'] for rc in registered_classifications]

    return classifier_list

def plot_results(talkers,classifiers,savefig=False):

    plt.subplot(111)

    x,y,s = [],[],[]

    count_talkers = Counter(talkers)
    count_classifiers = Counter(classifiers)

    for k in count_talkers:
        if count_classifiers.has_key(k):
            x.append(count_talkers[k])
            y.append(count_classifiers[k])

    xmin = np.min(x)
    xmax = np.max(x)
    ymin = np.min(y)
    ymax = np.max(y)

    plt.hexbin(x,y,gridsize=(20,20),bins='log',cmap=plt.cm.viridis)
    plt.axis([xmin,xmax,ymin,ymax])
    cb = plt.colorbar()
    cb.set_label(r'$\log_{10} N$')

    plt.xlabel(r'$N_{talk comments}$',fontsize=25)
    plt.ylabel(r'$N_{classifications}$',fontsize=25)

    plt.tight_layout()
    if savefig:
        plt.savefig('talk_contributions_{0}.png'.format(project_name))
    else:
        plt.show()

    return None

def print_results(talkers,classifiers):

    nt = len(set(talkers))
    nc = len(set(classifiers))
    percent = nt * 1./nc
    print "\n{0:.0f}% participation rate - {1} Talk participants out of {2} {3} classifiers".format(percent*100,nt,nc,project_name)

    return None

if __name__ == "__main__":

    classifications,projects,discussions = load_data()

    talkers = get_talkers(projects,discussions)
    classifiers = get_classifiers(classifications)

    plot_results(talkers,classifiers,savefig=False)
    print_results(talkers,classifiers)

