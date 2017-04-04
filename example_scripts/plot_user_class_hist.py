'''
This program takes a list of classification counts per user and makes a histogram
of it. It decides whether to make the axes logarithmic based on the data, but
it's not otherwise that complicated.

It's probably best if you run basic_project_stats.py beforehand, because this will
take one of the output files from that program.
'''

import sys, os
# imports continue below

# put this way up here so if there are no inputs we exit quickly before even trying to load everything else
try:
    classfile_in = sys.argv[1]
except:
    print("\nUsage: %s nclass_user_infile" % sys.argv[0])
    print("      nclass_user_infile is a csv file with a list of users and classification counts.")
    print("      it is assumed to be formatted as the nclass_user output csv from")
    print("      basic_project_stats.py, just 'user_name,n_class' on each line")
    print("      with NO header row. ")
    print("  Optional extra input (no spaces):")
    print("    outfile=filename.png")
    print("       specify the name of the output plot. If not specified, it will")
    print("       be based on the input filename, e.g. if your input file is")
    print("       my-project-nclass_user.csv, the output file name will be")
    print("       my-project-nclass_user_hist.png and .pdf.")
    sys.exit(0)

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt



plt.rc('figure', facecolor='none', edgecolor='none', autolayout=True)
plt.rc('path', simplify=True)
plt.rc('text', usetex=True)
plt.rc('font', family='serif')
plt.rc('axes', labelsize='large', facecolor='none', linewidth=0.7, color_cycle = ['k', 'r', 'g', 'b', 'c', 'm', 'y'])
plt.rc('xtick', labelsize='medium')
plt.rc('ytick', labelsize='medium')
plt.rc('lines', markersize=4, linewidth=1, markeredgewidth=0.2)
plt.rc('legend', numpoints=1, frameon=False, handletextpad=0.3, scatterpoints=1, handlelength=2, handleheight=0.1)
plt.rc('savefig', facecolor='none', edgecolor='none', frameon='False')

params =   {'font.size' : 11,
            'xtick.major.size': 8,
            'ytick.major.size': 8,
            'xtick.minor.size': 3,
            'ytick.minor.size': 3,
            }
plt.rcParams.update(params)




outplot_nclass = 'nclass_hist.png'

# check for other command-line arguments
if len(sys.argv) > 2:
    # if there are additional arguments, loop through them
    for i_arg, argstr in enumerate(sys.argv[2:]):
        arg = argstr.split('=')

        if arg[0]   == "outfile":
            outplot_nclass = arg[1]
            if outplot_nclass.endswith(".pdf"):
                # we'll write both but this will make the code cleaner later
                outplot_nclass = outplot_nclass.replace(".pdf", ".png")
            elif outplot_nclass.endswith(".png"):
                pass
            else:
                outplot_nclass += ".png"


#################################################################################
#################################################################################
#################################################################################


# Get the Gini coefficient - https://en.wikipedia.org/wiki/Gini_coefficient
#
# The Gini coefficient measures inequality in distributions of things.
# It was originally conceived for economics (e.g. where is the wealth in a country?
#  in the hands of many citizens or a few?), but it's just as applicable to many
#  other fields. In this case we'll use it to see how classifications are
#  distributed among classifiers.
# G = 0 is a completely even distribution (everyone does the same number of
#  classifications), and ~1 is uneven (~all the classifications are done
#  by one classifier).
# Typical values of the Gini for healthy Zooniverse projects (Cox et al. 2015) are
#  in the range of 0.7-0.9.
#  That range is generally indicative of a project with a loyal core group of
#    volunteers who contribute the bulk of the classification effort, but balanced
#    out by a regular influx of new classifiers trying out the project, from which
#    you continue to draw to maintain a core group of prolific classifiers.
# Once your project is fairly well established, you can compare it to past Zooniverse
#  projects to see how you're doing.
#  If your G is << 0.7, you may be having trouble recruiting classifiers into a loyal
#    group of volunteers. People are trying it, but not many are staying.
#  If your G is > 0.9, it's a little more complicated. If your total classification
#    count is lower than you'd like it to be, you may be having trouble recruiting
#    classifiers to the project, such that your classification counts are
#    dominated by a few people.
#  But if you have G > 0.9 and plenty of classifications, this may be a sign that your
#    loyal users are -really- committed, so a very high G is not necessarily a bad thing.
#
# Of course the Gini coefficient is a simplified measure that doesn't always capture
#  subtle nuances and so forth, but it's still a useful broad metric.

def gini(list_of_values):
    sorted_list = sorted(list_of_values)
    height, area = 0, 0
    for value in sorted_list:
        height += value
        area += height - value / 2.
    fair_area = height * len(list_of_values) / 2
    return (fair_area - area) / fair_area



# the output of basic_project_stats.py that we're assuming you're using has
# no header, so assume that's the case here.
# just keep in mind the "user_name" column is just an identifier, i.e. it could
# be the IP address, or an id based on IP and browser session, etc etc.
class_counts = pd.read_csv(classfile_in, header=None, names='user_name n_class'.split())

# basic stats
n_min_all = min(class_counts.n_class)
n_max_all = max(class_counts.n_class)

n_mean_all   =   np.mean(class_counts.n_class)
n_median_all = np.median(class_counts.n_class)

# decide whether we'll need to use a log axis or not
if (n_max_all - n_min_all) < 100:
    use_log = False
else:
    use_log = True

# separate into logged-in and not-logged-in
not_logged_in = np.array([q.startswith("not-logged-in") for q in class_counts.user_name])
is_logged_in  = np.invert(not_logged_in)

# if this file doesn't have not-logged-in users, we'll make plots slightly differently
if sum(not_logged_in) == 0:
    include_nologin = False
else:
    include_nologin = True

# logged-in basic stats
n_min_login = min(class_counts.n_class[is_logged_in])
n_max_login = max(class_counts.n_class[is_logged_in])

n_mean_login   =   np.mean(class_counts.n_class[is_logged_in])
n_median_login = np.median(class_counts.n_class[is_logged_in])

# not-logged-in basic stats
if include_nologin:
    n_min_nologin = min(class_counts.n_class[not_logged_in])
    n_max_nologin = max(class_counts.n_class[not_logged_in])

    n_mean_nologin   =   np.mean(class_counts.n_class[not_logged_in])
    n_median_nologin = np.median(class_counts.n_class[not_logged_in])



fig = plt.figure(figsize=(5,4))
axh = fig.add_subplot(1,1,1)

if use_log:

    # okay this is here because theoretically we might want this to be different
    # even though right now it's not.
    bins_all = np.arange(1, n_max_all, 1)

else:
    # the max classification count per user doesn't go above 100 so keep it simple
    bins_all = np.arange(1, n_max_all, 1.)

nclass_arr_login = np.array(class_counts.n_class[is_logged_in])
nclass_arr_all   = np.array(class_counts.n_class)

qhist_all   = axh.hist(nclass_arr_all,   bins=bins_all, histtype='stepfilled', color='k', alpha=0.2, label='All classifiers')
qhist_login = axh.hist(nclass_arr_login, bins=bins_all, histtype='stepfilled', color='blue', alpha=0.5, label='Logged-in classifiers')

hist_max = max(qhist_all[0])

if use_log:
    axisfac_x = 1.3
    xmin = 0.8
else:
    axisfac_x = 1.1
    xmin = 0.0

if hist_max > 1500.:
    use_log_y = True
    axisfac_y = 1.3
    ymin = 0.6
else:
    use_log_y = False
    axisfac_y = 1.1
    ymin = 0.0

axh.set_xlim(xmin, n_max_all * axisfac_x)
axh.set_ylim(ymin, hist_max  * axisfac_y)

if use_log:
    plt.gca().set_xscale("log")

# use_log only refers to the x-axis
if use_log_y:
    plt.gca().set_yscale("log")

axh.set_xlabel('Classification count by user', fontsize=11)
axh.set_ylabel('User count', fontsize=11)
axh.legend(frameon=False, loc='upper right', fontsize=11)

plt.savefig(outplot_nclass, frameon=False, bbox_inches='tight', pad_inches=0.1, transparent=True)
plt.savefig(outplot_nclass.replace('.png', '.pdf'), frameon=False, bbox_inches='tight', pad_inches=0.1, transparent=True)

plt.cla()
plt.close('All')

print("Histograms written to %s and .pdf" % outplot_nclass)



#end
