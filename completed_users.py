from pymongo import MongoClient
from bson.objectid import ObjectId
import requests

# Report the number and user_names of people who have completed various groups in Galaxy Zoo

client = MongoClient('localhost',27017)
ouroboros = client['ouroboros']
users = ouroboros['users']

galaxy_zoo = client['galaxy_zoo']
classifications = galaxy_zoo['classifications']

r = requests.get('https://api.zooniverse.org/projects/galaxy_zoo/groups')
groups = r.json()

for group in groups:
    completed_users = []
    no_username_found = 0
    n = len(group['completed_by'])
    for objid in group['completed_by']:
        x = users.find_one({"_id":ObjectId(objid)})
        if x == None:
            c = classifications.find_one({'user_id':ObjectId(objid)})
            if c == None:
                no_username_found += 1
            else:
                completed_users.append(c['user_name'])
                #print "UserId {0} from Galaxy Zoo is {1}".format(objid,c['user_name'])
        else:
            completed_users.append(x['name'])
            #print "UserId {0} from Ouroboros is {1}".format(objid,x['name'])
    
    if n > 0:
        print "\n{0} users are marked as completed for {1}.".format(n,group['name'])
        print "\t{0}".format(",".join(completed_users))
        if no_username_found > 0:
            print "\t{0} `user_ids` marked as completed for {1}, but no matching `user_name` found in Ouroboros or Galaxy Zoo".format(no_username_found,group['name'])
    else:
        print "\nNo users are marked as completed for {0}.".format(group['name'])

