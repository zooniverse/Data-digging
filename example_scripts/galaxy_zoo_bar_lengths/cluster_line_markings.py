# um so I never ran this at the command line
# only ever used ipython (4.2.0) for it
# probably means I should make this a notebook
import sys, os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
#import json
from datetime import datetime
from scipy.cluster.hierarchy import dendrogram, linkage, fcluster

# Note: this is the markfile_out from extract_line_drawings.py
# one row per line mark, so if a person draws 3 lines during a classification that will make it 3 rows in this file.
# Hopefully they'll only draw 2 because that's what we asked for but, who knows?
linefile_in = 'galaxy-zoo-bar-lengths-line-drawings.csv'

try:
    cluster_method = sys.argv[1]
except:
    cluster_method = 'average'

all_lines_out       = 'gzbl_line_marks_raw_with_clusters_%s.csv' % cluster_method
clustered_lines_out = 'gzbl_line_marks_only_with_clusters_%s.csv' % cluster_method
clusters_out        = 'gzbl_clusters_all_%s.csv' % cluster_method


# read the file into line_marks
line_marks_all = pd.read_csv(linefile_in)
print("Read %d entries from %s ..." % (len(line_marks_all), linefile_in))
# this should have the columns:
#'classification_id subject_id user_name user_id user_ip created_at workflow_id workflow_version x1 x2 y1 y2 slope intercept length i_tool'.split()

# this returns values from -pi to pi
#line_marks['angle'] = [np.arctan(q) for q in line_marks.slope]
line_marks_all['angle'] = np.arctan(line_marks_all.slope)

# we will need these later, in cluster_oneid()
line_marks_all['cluster_id'] = line_marks_all.x1 * 0 - 1
line_marks_all['d_max']      = line_marks_all.x1 * 0.00 + 1.0e-6

# 0-length lines should not be included in the clustering
line_marks = line_marks_all[line_marks_all.length > 1.]

# initialize this
all_linkages = {}

# people can draw in any order so we need to sort these so each line has the same definition of the pivot point/angle
# this takes a little while
#thelines = pd.DataFrame([sort_points(q[1]) for q in line_marks['x1 y1 x2 y2 slope length angle user_name classification_id'.split()].iterrows()])

#thelines = pd.DataFrame([sort_points(q[1]) for q in themarks['x1 y1 x2 y2 slope length angle'.split()].iterrows()])


# here we need to groupby subject_id and then run through the group and in a function apply the clustering to each.



def make_dendrograms(line_marks):
    all_ids = line_marks.subject_id.unique()
    n_ids = len(all_ids)

    for i_id, theid in enumerate(all_ids):
        #print(theid)
        themarks_unsort = line_marks[line_marks.subject_id == theid]
        themarks = pd.DataFrame([sort_points(q[1]) for q in themarks_unsort['x1 y1 x2 y2 slope length angle user_name classification_id'.split()].iterrows()])

        cluster_oneid(themarks, theid)

        if i_id % 100 == 0:
            print("Count: %d of %d at %s" % (i_id, n_ids, str(datetime.now())))




# Below is just clustering for one.

def cluster_oneid(themarks, theid):

    if len(themarks) < 3:
        return

    # we aren't going to track individual users, but we will track counts
    # ugh, I forgot that there are some duplicates here, so count classification_id, not user_name, as in some cases n_class > n_user
    the_users = themarks['classification_id'].unique()
    n_users = len(the_users)

    if n_users < 3:
        return

    thelines = themarks['x1 y1 length angle'.split()].copy()

    # don't consider lines that were obvious accidental clicks (zero-length)
    #real_lines = thelines_all.length > 1.
    #thelines = thelines_all[real_lines]

    # see if we need to do an angle transform
    # not written for now

    # perform the clustering
    # I've looked at examples of single, complete, average and ward
    the_linkage = linkage(thelines, cluster_method)

    # use the fact we know we're looking for 2 clusters in a system where all the volunteers understood the task, followed instructions and each drew 2 lines
    # i.e. the number of points in each cluster should be about equal, and
    # no cluster should have much more than half the total number of points

    # though actually I should just make sure there aren't any clusters with more points than the number of users... not sure how to do that except to do a groupby early on, pick out len(users.unique()) in each group, then do a left join back up on the markings DF
    # nah I can just pass it through to the function, right?

    first_cut_linkage = the_linkage[(the_linkage[:,3] <= n_users)]
    # Let's include the last dendrogram level that meets that criterion, so let's see what happens
    # if any of the cluster sizes exceeds n_users, keep decreasing the distance until that is not so
    i_dist = -1
    cl_sizes = pd.Series([n_users +1]) # make sure it actually enters the loop
    while (sum(cl_sizes > n_users) > 0):
        d_guess = first_cut_linkage[:,2][i_dist] + .01

        clusters = pd.DataFrame(fcluster(the_linkage, d_guess, criterion='distance'))
        clusters.columns = ['cluster_id']
        clusters['count'] = clusters.cluster_id * 0.0 + 1.0
        by_cluster = clusters.groupby('cluster_id')
        cl_sizes = by_cluster['count'].aggregate('sum')

        #print(i_dist, d_guess)

        i_dist -= 1

    i_dist += 1

    plot_dendrogram(the_linkage, theid, d_guess)

    all_linkages[str(theid)] = the_linkage

    # now record the cluster id in the marks
    themarks['cluster_id'] = [q for q in clusters.cluster_id]
    themarks['d_max'] = [d_guess for q in clusters.cluster_id]

    is_these_marks = line_marks_all.index.isin(themarks.index)

    # I never manage to format this line right
    #line_marks_all.loc[is_these_marks, 'cluster_id d_max'.split()] = [themarks.cluster_id, themarks.d_max]

    # add the cluster IDs and d_max value back to the original line marks DF
    line_marks_all.loc[is_these_marks, 'cluster_id'] = themarks.cluster_id
    line_marks_all.loc[is_these_marks, 'd_max'] = themarks.d_max



    #print("Finally: %d" % i_dist)

    return




def plot_dendrogram(the_linkage, theid, d_max):
    fig = plt.figure(figsize=(12, 5))

    axL = fig.add_subplot(1,2,1)

    axL.set_title('Hierarchical %s Clustering Dendrogram' % cluster_method)
    axL.set_xlabel('sample index')
    axL.set_ylabel('distance')
    dendrogram(
        the_linkage,
        leaf_rotation=90.,  # rotates the x axis labels
        leaf_font_size=8.,  # font size for the x axis labels
    )
    # freeze the current xlimits
    xlimits = axL.get_xlim()

    axL.plot(xlimits, np.array([d_max, d_max]), linestyle='-', color="#777777")

    axL.set_xlim(xlimits)


    axR = fig.add_subplot(1,2,2)
    axR.plot(the_linkage[:,2])
    # freeze the current ylimits
    xlimits = axR.get_xlim()
    axR.plot(xlimits, np.array([d_max, d_max]), linestyle='-', color="#777777")

    axR.set_xlim(xlimits)

    axR.set_xlabel('iteration')
    axR.set_ylabel('distance')

    plt.tight_layout()

    plt.savefig('dendrograms/dendrogram_%s_%s.png' % (theid, cluster_method), facecolor='None', edgecolor='None')
    #plt.show()
    plt.clf()
    plt.cla()
    plt.close('')
    plt.close('All')



def sort_points(theline):

    # just sort by x - sort_points_old does something more complicated but we don't need it here
    if float(theline.x2) < float(theline.x1):
        theline.y1, theline.y2 = theline.y2, theline.y1
        theline.x1, theline.x2 = theline.x2, theline.x1

    return theline


def sort_points_old(theline):
    # we can have a few cases:
    # non-vertical lines: just sort so the lowest-x coordinate is in (x1, y1)
    # (close-to-)vertical lines: sort so that the lowest-y coordinate is in (x1, y1)
    # Let's say if |slope| > 1 (45 degrees) then we do the y coordinate.

    # hang on... actually if the slope is right around -1 here then I'll get random swapping of directions, which is not great.
    # maybe I can add in something special for slopes around -1

    if np.abs(theline.slope) > 1.0:
        if float(theline.y2) < float(theline.y1):
            # apparently you can use tuples to swap. Yay, no dummy variables
            theline.y1, theline.y2 = theline.y2, theline.y1
            theline.x1, theline.x2 = theline.x2, theline.x1
    else:
        if float(theline.x2) < float(theline.x1):
            theline.y1, theline.y2 = theline.y2, theline.y1
            theline.x1, theline.x2 = theline.x2, theline.x1

    return theline['x1 y1 x2 y2 slope length angle'.split()]



# determines the consensus value for each cluster
def aggregate_clusters(grp):
    # just make really sure they're sorted
    themarks_unsort = pd.DataFrame(grp)
    themarks = pd.DataFrame([sort_points(q[1]) for q in themarks_unsort.iterrows()])
    by_cluster = themarks.groupby('cluster_id')
    lines_per_cluster = by_cluster.x1.aggregate('count')
    x1_avg = by_cluster.x1.apply(lambda x: np.mean(x))
    x2_avg = by_cluster.x2.apply(lambda x: np.mean(x))
    y1_avg = by_cluster.y1.apply(lambda x: np.mean(x))
    y2_avg = by_cluster.y2.apply(lambda x: np.mean(x))

    x1_med = by_cluster.x1.apply(lambda x: np.median(x))
    x2_med = by_cluster.x2.apply(lambda x: np.median(x))
    y1_med = by_cluster.y1.apply(lambda x: np.median(x))
    y2_med = by_cluster.y2.apply(lambda x: np.median(x))

    n_class = lines_per_cluster*0.0 + float(len(themarks.classification_id.unique()))
    p_true_positive = lines_per_cluster.astype(float)/n_class


    cluster_meas = {}
    cluster_meas["lines_in_cluster"] = lines_per_cluster
    cluster_meas["x1_avg"]           = x1_avg
    cluster_meas["x2_avg"]           = x2_avg
    cluster_meas["y1_avg"]           = y1_avg
    cluster_meas["y2_avg"]           = y2_avg
    cluster_meas["x1_med"]           = x1_med
    cluster_meas["x2_med"]           = x2_med
    cluster_meas["y1_med"]           = y1_med
    cluster_meas["y2_med"]           = y2_med
    cluster_meas["n_class_total"]    = n_class
    cluster_meas["p_true_positive"]  = p_true_positive
    cluster_meas = pd.DataFrame(cluster_meas)

    return cluster_meas









# actually run things
# this will take a while (maybe an hour?)
print("Performing clustering analysis using %s distance on all subjects..." % cluster_method)
make_dendrograms(line_marks)
print("     ...done performing clustering. Cleaning up non-detections,")
print("        then writing raw marks back to new file.")

# the result of make_dendrograms() is to update line_marks_all with cluster identifications and the d_max value used, for each mark.
# first let's throw out the marks that didn't get used in a cluster identification (sometimes there just weren't enough classifications of "Yes, it has a bar") to aggregate
line_marks = line_marks_all[line_marks_all.cluster_id >= 0.]

# but write both versions to files
line_marks_all.to_csv(all_lines_out)
line_marks.to_csv(clustered_lines_out)

by_subj = line_marks.groupby('subject_id')

# now actually make the aggregated cluster outputs
# takes a few minutes (up to 10?)
print("Aggregating clusters to determine consensus marks...")
clusters_all = by_subj.apply(aggregate_clusters)
print("...done. Printing to outfile.")

clusters_all.to_csv(clusters_out)

# we still need to compute the consensus line measurement for each cluster, as well as some stats on that cluster (mainly counting up the classification_ids that are members of that cluster and reporting that as a fraction of n_classifications for that subject)











#end
