import sys, os, csv
'''
This is an aggregation of the Exoplanet Explorers project now that the exports 
have gotten pretty big (currently 16 GB) and pandas alone isn't going to deal 
with this on a normal laptop or desktop.

It takes as a starting point that each subject can be aggregated independently. 

KEY POINT: it requires that the aggregations export be sorted by subject id.

Sorting a large text file can be a resource-intensive task, and for the above 
file the sort takes longer than running the program below, but the sort is 
easier for my machine to cope with than trying to run the standard aggregation 
via reading the entire export file into a pandas dataframe.

Don't try to use a spreadsheet program like Excel to sort a big CSV file!
You could try the command line, e.g.

%> sort -t "," -n -k 14 exoplanet-explorers-classifications.csv > exoplanet-explorers-classifications-sortbysubjectid.csv 

but I have not tried that myself and I'm not sure how well the sort command 
parses lines such that e.g. it knows a comma inside a quote isn't actually a 
field separator. If it doesn't know that then this command won't work because
the subject id column (column #14) is at the end of the file after the JSON 
fields that contain the annotations and the subject metadata, both of which 
may have lots of (and variable numbers of) commas.

Also the sort command doesn't handle header lines well so I guess you'd need
something more like:

%> head -n1 exoplanet-explorers-classifications.csv > headertemp.txt 
%> tail -n +2 exoplanet-explorers-classifications.csv | sort -t "," -n -k 14 > classifications_noheaders_sorted.csv
%> cat headertemp.txt classifications_noheaders_sorted.csv > exoplanet-explorers-classifications-sortbysubjectid.csv 
%> rm headertemp.txt classifications_noheaders_sorted.csv 

Note that at one point this requires you to have disk space for 3 copies of the 
file: original, sorted-but-no-headers, sorted-with-headers.

Instead, I have had good luck doing this sort in TOPCAT, available at
http://www.star.bris.ac.uk/~mbt/topcat/
TOPCAT had no problems reading the above file and performing the sort by
subject id using 3 GB of allocated memory (and it probably could have done it 
with less). It took some time, about 2 hours including re-exporting the file 
back to my laptop, but it didn't crash.

There are more clever ways of sorting things too, but TOPCAT worked for me so I 
didn't really explore further.

-Brooke Simmons, 18 Nov 2019
'''
# default infile - actually this default isn't used, you still have to specify it, but it's a suggestion
infile_default = 'exoplanet-explorers-classifications-sortbysubjectid.csv'
# default outfile
outfile_default = 'exoplanet-explorers-aggregations.csv'
# rankfile_stem = 'subjects_ranked_by_weighted_class_asof_'

try:
    classfile_in = sys.argv[1]
except:
    #classfile_in = 'exoplanet-explorers-classifications.csv'
    print("\nUsage: %s classifications_infile [aggregations_outfile]" % sys.argv[0])
    print("      classifications_infile is a Zooniverse (Panoptes) classifications data export CSV,\n    except sorted by subject ID, e.g. %s " % infile_default)
    # print("      weight_class is 1 if you want to calculate and apply user weightings, 0 otherwise.")
    print("      aggregations_outfile is the name of the file you want written. If you don't specify,")
    print("          the filename is %s by default." % outfile_default)
    sys.exit(0)


import numpy as np
import pandas as pd
#import datetime
#import dateutil.parser
import ujson
import random
import gc


############ Define files and settings below ##############



active_workflow_ids = [3821, 5800]
# active_workflow_ids = [3821]
# active_workflow_ids = [5800]

# anything with fewer classifications than this number won't be printed out to the final aggregations file
# nclass_min = 1.
nclass_min = 5.

# This program doesn't know how many subjects there are until it's aggregated them all, so this is a best
# guess at a decent interval to print progress
n_print_every = 10000

try:
    aggfile_out = sys.argv[2]
except:
    aggfile_out = outfile_default



# initialize a new aggregation dictionary
# this is project-specific and this is a very simple workflow (just 1 Y/N question task)
# also I'm using "initialise" too below; please forgive this UK/US transplant
def get_new_agg():

    theagg_subj = {
        'n_class'  :  0.0,
        'n_yes'    :  0.0,
        'f_yes'    :  0.0,
        'workflows': []
    }

    return theagg_subj



# add 1 classification to the ongoing aggregation
def aggregate_addclass(theclass, theagg_subj, i_csv, getfrac=False):

    # we're just going to assume this is the correct subject
    # this_subject_id = theclass[i_csv['subject_id']]

    this_anno       = ujson.loads(theclass[i_csv['annotations']])

    # get the Y/N is it a transit label
    # NOTE this is project-specific and currently it's the only task we're aggregating
    for task in this_anno:
        if task['task'] == 'T0':
            this_answer = task['value']
            break

    theagg_subj['n_class'] += 1.0

    if this_answer == 'Yes':
        theagg_subj['n_yes'] += 1.0

    # this is just checking that we're not accidentally aggregating across multiple workflows
    # that is, right now we definitely can do that and maybe we don't even mind
    # but this will keep a record of what workflows are being aggregated together
    # so that if you do mind you can do something about it
    the_wfid = int(theclass[i_csv['workflow_id']])
    if the_wfid not in theagg_subj['workflows']:
        theagg_subj['workflows'].append(the_wfid)

    # get the running (or possibly the final) fraction, if requested
    # technically we don't need to do this until we know it's the final classification for this subject
    # so as we sometimes have >100 classifications per subject I'm skipping this by default
    if getfrac:
        theagg_subj['f_yes'] = theagg_subj['n_yes']/theagg_subj['n_class']

    return theagg_subj





def breakout_metadata(row):

    ind = row[0]
    # the subject metadata is weird, it is a json with 1 top-level key, which is the subject id
    # and subject id is the index of the DF row, so we need to extract that and then use it to get the rest of the content
    themeta = ujson.loads(row[1]['subject_data'])
    thesubject = themeta[ind]
    # also keep the subject_id in the data here so we can use it as an index later
    thesubject['subject_id'] = ind

    return pd.Series(thesubject)




############# End definitions of files and settings, start main work  ################




i_subj = 1

with open(classfile_in, "rb") as f:

    reader = csv.reader(f)
    header = next(reader) # first line is the header line, so keep it as a reference
    print("CSV header: {}".format(header))

    # CSV header: ['classification_id', 'user_name', 'user_id', 'user_ip', 'workflow_id', 'workflow_name', 'workflow_version', 'created_at', 'gold_standard', 'expert', 'metadata', 'annotations', 'subject_data', 'subject_ids']
    # let's get some indices we will need
    # note list.index() is not that efficient but since we're only running it once for the whole table it's ok here
    i_csv = {
        'classification_id' : header.index('classification_id'),
        'user_name'         : header.index('user_name'),
        'user_id'           : header.index('user_id'),
        'created_at'        : header.index('created_at'),
        'workflow_id'       : header.index('workflow_id'),
        'workflow_version'  : header.index('workflow_version'),
        'annotations'       : header.index('annotations'),
        'subject_data'      : header.index('subject_data'),
        'subject_id'        : header.index('subject_ids')
    }


    # need to read the first line of data in to get initial material to start with
    theclass = next(reader)
    this_subject_id = theclass[i_csv['subject_id']]

    # start a dictionary for aggregated information
    # the entire dictionary for all subjects, where the key will be the subject id
    theagg = {}
    # just this subject's aggregated information
    theagg_subj = get_new_agg()

    the_wfid = int(theclass[i_csv['workflow_id']])
    # the_wfv  = int(float(theclass[i_csv['workflow_version']]))  # major version only

    if the_wfid in active_workflow_ids:
        # fill the dictionary with the results of this classification
        theagg[this_subject_id] = aggregate_addclass(theclass, theagg_subj, i_csv)

    # now iterate through lines and keep aggregating stats until we've reached a new subject
    for theclass in reader:
        new_subject_id = theclass[i_csv['subject_id']]
        the_wfid = int(theclass[i_csv['workflow_id']])

        if new_subject_id != this_subject_id:
            # the old subject ID aggregation was updated in the last iteration so we don't need to do it here
            # but we can add the subject_data to the dictionary
            theagg[this_subject_id]['subject_data'] = lastclass[i_csv['subject_data']]
            # now that we know we're done, get the fraction of classifiers who said yes
            theagg[this_subject_id]['f_yes'] = theagg[this_subject_id]['n_yes']/theagg[this_subject_id]['n_class']
            # and then update the subject id to the current one before starting the new aggregation
            this_subject_id = new_subject_id
            # it's a new subject so we need to initialise the new aggregation
            theagg_subj = get_new_agg()
            i_subj += 1

            if i_subj % n_print_every == 0:
                print("Beginning aggregation for subject %d (id %d)" % (i_subj, int(this_subject_id)))
        else:
            pass

        # we only care about this classification if it's in the workflows we previously identified
        if the_wfid in active_workflow_ids:
            # take the existing aggregation and update it with the results of this classification
            #
            # note this worked as a single line, updating theagg[this_subject_id] directly
            # even though I fed in theagg_subj and never updated that explicitly
            # so sending a dictionary to a function must be sending a memory pointer (unlike a variable)
            # I have made it explicit, however, because I don't want this to silently break later
            # if that behaviour changes in some later version of Python
            # sometimes I really miss ANSI C. just saying
            theagg_subj = aggregate_addclass(theclass, theagg_subj, i_csv)
            theagg[this_subject_id] = theagg_subj
        
        # this is a useful way to make a copy of a list (.copy() only works in python 3+)
        lastclass = theclass[:]


        # end check if this classification is in a workflow we want to aggregate
    # end loop through lines in the CSV file

    # this needs doing for the current subject even if the most recent classification for it wasn't in the active workflow list
    theagg[this_subject_id]['subject_data'] = theclass[i_csv['subject_data']]

# end with open(file) as f

f.close() 

print("Aggregated %d subjects, now extracting subject metadata and printing..." % i_subj)

# translating the dictionary into a pandas dataframe is going to make the next steps easier
aggregation_df = pd.DataFrame.from_dict(theagg, orient='index')


# the next steps in particular are to break out the subject data into new columns
# this next thing is now done in the breakout_metadata() function
# aggregation_df['meta_json'] = [ujson.loads(q) for q in aggregation_df['subject_data']]

# this line is probably the biggest CPU cycle ask of the whole program
temp = [breakout_metadata(q) for q in aggregation_df.iterrows()]
subj_data = pd.DataFrame(temp)
subj_data.set_index('subject_id', inplace=True)

# subj_data should be in row-for-row order with aggregation_df but also they're indexed properly so it should match properly
# note if you get all NaNs in the subject data columns after running this but you know subj_data is filled, it's likely an indexing issue
aggregation_df[subj_data.columns.tolist()] = subj_data

# make sure the index has a name so that when it prints as a column the name won't be blank
aggregation_df.index.name = 'subject_id'

# put the columns in the order we want to print them
# in such a way as to be agnostic to whatever the individual subject metadata columns are
allcols_orig = aggregation_df.columns.tolist()
thecols = allcols_orig[:]  # make a copy

# could just take theagg_subj.keys() but then we couldn't control the ordering
first_cols = ['n_class', 'n_yes', 'f_yes', 'workflows']

for q in first_cols:
    thecols.remove(q)

thecols.remove('subject_data')

# we want to print the aggregation info first, then the individual metadata columns,
# then the original json column just in case we need to track something down later
print_cols = first_cols + thecols + ['subject_data']

# it's possible we've got subjects in the aggregation that were entirely in non-active workflows
# so they may have been initialised and passed through to the DF, but have no actual information
has_class = aggregation_df['n_class'] >= nclass_min

print("Following aggregations, %d of %d total subjects have at least %d classifications in workflows:" % (sum(has_class), len(has_class), nclass_min))
print(active_workflow_ids)

# print to the file
print("Printing these aggregations to %s ..." % (aggfile_out))
aggregation_df[print_cols][has_class].to_csv(aggfile_out)



#done 