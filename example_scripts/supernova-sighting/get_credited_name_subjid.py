import sys, os, ujson, pandas as pd
from panoptes_connect import panoptes_connect
from panoptes_client import User



def get_credited_name_all(vols, whichtype='user_id'):
    x = panoptes_connect()

    disp_names = vols.copy()
    i_print = int(len(vols)/10)
    if i_print > 1000:
        i_print = 1000
    elif i_print < 10:
        i_print = 10

    if whichtype == 'user_id':
        # user ID lookup has a different format for the query
        for i, the_id in enumerate(vols):
            user = User.find(int(the_id))
            name_use = user.credited_name
            if name_use == '':
                name_use = user.display_name
                if name_use == '':
                    name_use = user.login

            disp_names.loc[(vols==the_id)] = name_use
            #credited_names[the_id] = user.credited_name
            if i % i_print == 0:
                print("Credited name: lookup %d of %d (%s --> %s)" % (i, len(vols), the_id, name_use))

    else:
        # if we're here we don't have user ID but presumably do have login
        for i, the_login in enumerate(vols):
            name_use = the_login
            for user in User.where(login=the_login):
                name_use = user.display_name
            #credited_names[the_login] = cname
            disp_names.loc[(vols==the_login)] = name_use
            if i % i_print == 0:
                print("Credited name: lookup %d of %d (%s --> %s)" % (i, len(vols), the_login, name_use))



    return disp_names


classifications = pd.read_csv('supernova-sighting-classifications-wfid3638v16-nodup-sglonly.csv')


classifications['anno_json'] = [ujson.loads(q) for q in classifications.annotations]
classifications['answer'] = [q[0]['value'] for q in classifications.anno_json]


ids_of_interest = [21594033, 21528871, 21561104, 21528903]
names_of_interest=['AAT',   '2p3m',   '18ch',   '18as']

users_allobjs = {}

for i, id in enumerate(ids_of_interest):
    thename = names_of_interest[i]
    theclass = classifications['user_name user_id answer subject_ids'.split()][classifications.subject_ids == id]
    logged_in = np.invert([q.startswith('not-logged-in') for q in theclass.user_name])
    if thename == 'AAT':
      affirmative = (theclass.answer == "Yes") | (theclass.user_name == "Axe26")
    else:
      affirmative = (theclass.answer == "Yes")

    theclass_reg = theclass[logged_in & affirmative].copy()
    theclass_reg['credited_name'] = get_credited_name_all(theclass_reg['user_id'].astype(int))
    theclass_reg['user_id'] = pd.to_numeric(theclass_reg.user_id, errors='coerce', downcast='integer')
    theclass_reg.set_index('user_id', inplace=True)
    users_allobjs[thename] = theclass_reg.copy()
    outname = 'YES_subj%d_source%s_withcreditedname.csv' % (id, thename)
    theclass_reg.to_csv(outname)





#bye
