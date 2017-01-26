# um so I never ran this at the command line
# only ever used ipython (4.2.0) for it
# probably means I should make this a notebook
import sys, os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
#import json
from datetime import datetime
#from scipy.cluster.hierarchy import dendrogram, linkage, fcluster

try:
    cluster_method = sys.argv[1]
except:
    cluster_method = 'average'


# Note: this is the clusters_out from cluster_line_markings.py
clusters_in        = 'gzbl_clusters_all_%s.csv' % cluster_method

# the file we'll write to when we've picked a length and width for each subject
lengths_widths_out = 'gzbl_lengths_widths_onepersubject_%s.csv' % cluster_method


###################################################
#
# define functions to get the angle between lines
#
###################################################

# use the dot product: A • B = x_A*x_B + y_A*y_B = length(A)*length(B)*cos(theta)
# so cos(theta) = (x_A*x_B + y_A*y_B)/(length(A)*length(B))
# so theta = acos(all that stuff right above)

def dot(vA, vB):
    return (vA[0]*vB[0]) + (vA[1]*vB[1])


def ang(vA, vB):
    # Vector needs to be in form
    # [xlength, ylength]
    # Get dot prod
    dot_prod = dot(vA, vB)
    # Get magnitudes
    magA = dot(vA, vA)**0.5
    magB = dot(vB, vB)**0.5
    # Get cosine value
    cos_ = dot_prod/magA/magB
    # Get angle in radians and then convert to degrees
    angle = np.arccos(cos_)
    # Basically doing angle <- angle mod 360
    ang_deg = np.degrees(angle)%360

    if ang_deg-180>=0:
        # As in if statement
        return 360 - ang_deg
    else:
        return ang_deg

###################################################
#
# Function that chooses length and width clusters
#
###################################################

# define some columns, but we won't ever use this specific list
ret_cols = "n_lines_highprob cluster_id p_true_positive line_size_pix_avg line_size_pix_med angle_lw_avg angle_lw_med x1_avg y1_avg x2_avg y2_avg x1_med y1_med x2_med y2_med".split()
loop_cols = ret_cols.copy()
# take out the list elements we won't loop through to add "width_" and "length_" to
loop_cols.remove("angle_lw_avg")
loop_cols.remove("angle_lw_med")
loop_cols.remove("n_lines_highprob")

def choose_width_length(grp):
    # because working with groups is slightly different than DFs and that's irritating
    # so just make it a DF
    thesubj = pd.DataFrame(grp)

    # sort so that the highest p_true_positive values are at the top of the DF
    thesubj.sort_values('p_true_positive', ascending=False, inplace=True)

    # lines we might pick out as possibly real and high-probability clusters
    high_p = thesubj.p_true_positive >= 0.3
    # ideally this is 2 but sometimes a cluster gets split and we want to flag those
    n_possible = sum(high_p)

    # start our DataFrame that we'll be returning with bar length and width lines
    LW_properties = pd.DataFrame([{"n_lines_highprob":n_possible}])

    # as long as there are at least 2 clusters we can use
    if len(thesubj) >= 2:
        # take the highest 2 p values and make those your length and width
        theclusters = thesubj.head(2)

        i_lw = {}
        # pick a length and a width based on length
        # I'm electing to use median length to be more robust to outliers
        if theclusters.line_size_pix_med[theclusters.index[0]] > theclusters.line_size_pix_med[theclusters.index[1]]:
            i_lw["L"] = theclusters.index[0]
            i_lw["W"] = theclusters.index[1]
            #i_length = theclusters.index[0]
            #i_width  = theclusters.index[1]
        else:
            i_lw["L"] = theclusters.index[1]
            i_lw["W"] = theclusters.index[0]
            #i_length = theclusters.index[1]
            #i_width  = theclusters.index[0]


        # get the angle between the 2 vectors
        # vec = [dx, dy] format to feed into the angle function
        vec1_avg = [(theclusters.x1_avg[i_lw["L"]] - theclusters.x2_avg[i_lw["L"]]), (theclusters.y1_avg[i_lw["L"]] - theclusters.y2_avg[i_lw["L"]])]
        vec2_avg = [(theclusters.x1_avg[i_lw["W"]] - theclusters.x2_avg[i_lw["W"]]), (theclusters.y1_avg[i_lw["W"]] - theclusters.y2_avg[i_lw["W"]])]

        vec1_med = [(theclusters.x1_med[i_lw["L"]] - theclusters.x2_med[i_lw["L"]]), (theclusters.y1_med[i_lw["L"]] - theclusters.y2_med[i_lw["L"]])]
        vec2_med = [(theclusters.x1_med[i_lw["W"]] - theclusters.x2_med[i_lw["W"]]), (theclusters.y1_med[i_lw["W"]] - theclusters.y2_med[i_lw["W"]])]

        angle_lw_avg = ang(vec1_avg, vec2_avg)
        angle_lw_med = ang(vec1_med, vec2_med)

        # add angles to DF before setting length/width specific properties
        LW_properties["angle_lw_avg"] = angle_lw_avg
        LW_properties["angle_lw_med"] = angle_lw_med

        for LW in ["L", "W"]:
            if LW == "L":
                LLWW = "length"
            else:
                LLWW = "width"

            # save everything as its own column, either length or width
            for meas in loop_cols:
                LW_properties["%s_%s" % (LLWW, meas)] = theclusters[meas][i_lw[LW]]

        # end "if there were at least 2 clusters detected"

    else:
        # there is 0 or 1 line and we can't really do much with that so just
        # call it a non-detection
        # this should be rare
        LW_properties["angle_lw_avg"] = -1
        LW_properties["angle_lw_med"] = -1

        ##############################################################
        #
        #    UNDETECTED LOOP - JUST RETURNING -1 FOR EVERYTHING
        for LW in ["L", "W"]:
            if LW == "L":
                LLWW = "length"
            else:
                LLWW = "width"
            for meas in loop_cols:
                LW_properties["%s_%s" % (LLWW, meas)] = -1.
        #
        #    UNDETECTED LOOP - JUST RETURNING -1 FOR EVERYTHING
        #
        ##############################################################


    # okay, return now
    return LW_properties




################################################

#               BEGIN MAIN

################################################


print("Reading clusters determined via %s method from %s..." % (cluster_method, clusters_in))
clusters_all = pd.read_csv(clusters_in)

# compute magnitude (lengths) of each clustered line (units of pixels)
# we will need these to choose which is a bar length and which is a width
clusters_all['line_size_pix_avg'] = np.sqrt((clusters_all.x1_avg - clusters_all.x2_avg)**2 + (clusters_all.y1_avg - clusters_all.y2_avg)**2)
clusters_all['line_size_pix_med'] = np.sqrt((clusters_all.x1_med - clusters_all.x2_med)**2 + (clusters_all.y1_med - clusters_all.y2_med)**2)

# Need to group by subject and then for each subject choose a length and width
cl_bysubj = clusters_all.groupby('subject_id')

print("Choosing length and width lines from aggregated clusters for each subjects...")
cl_lw_all = cl_bysubj.apply(choose_width_length)

print("  Printing outputs (1 line per subject) to %s ..." % lengths_widths_out)
cl_lw_all.to_csv(lengths_widths_out)


#booya
