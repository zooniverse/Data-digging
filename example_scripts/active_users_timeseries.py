'''

This program will calculate a timeseries of active users across the lifetime of a project (or a workflow id/version for a project).

The inputs needed are:
  the classification export file (request & download from the Project Builder)
  plus some optional inputs that are listed below.

The program takes snapshots of the classification timeline in units of hours or days, and over each time period it computes the number of classifications submitted, the number of classifiers (registered and unregistered) who submitted the classifications, and the time spent classifying by those users. It outputs these timeseries to a CSV file.

Brooke Simmons, 30th March 2017
updated 21st May 2017

'''

import sys, os

# put this way up here so if there are no inputs we exit quickly before even trying to load everything else
try:
    classfile_in = sys.argv[1]
except:
    print("\nUsage: %s classifications_infile" % sys.argv[0])
    print("      classifications_infile is a Zooniverse (Panoptes) classifications data export CSV.")
    print("  Optional extra inputs (no spaces):")
    print("    workflow_id=N")
    print("       specify the program should only consider classifications from workflow id N")
    print("    workflow_version=M")
    print("       specify the program should only consider classifications from workflow version M")
    print("       (note the program will only consider the major version, i.e. the integer part)")
    print("    outfile=filename.csv")
    print("       specify the name of the output file. If not specified, it will")
    print("       be based on the input filename, e.g. if your input file is")
    print("       my-project-classifications.csv, the output file name will be")
    print("       my-project-classifications_active_users_timeseries.csv.")
    print("    project=project_name")
    print("       For use labelling plots with the project name")
    print("    --time_spent")
    print("       if specified, the program will try to compute time actively spent")
    print("       classifying on the project using started_at and finished_at metadata")
    print("    --days")
    print("       compute stats by day rather than by hour")
    print("    --plots_only")
    print("       if specified, the program won't re-calculate the time series")
    print("       and will instead just read in the outfile and re-make plots.")
    sys.exit(0)


import numpy as np
import pandas as pd
import datetime
import dateutil.parser
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.gridspec as gridspec
import ujson
import gc
from gini import gini



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



# default value is not to care about workflow ID or version
workflow_id      = -1
workflow_version = -1

# assume no project name is specified
project_name = ""

# default mode is to calculate the timeseries afresh
plot_only = False

# default mode is to not worry about time spent classifying
time_spent = False

# default mode is to compute stats by the hour
dt_unit = 'h'

outfile = classfile_in.replace(".csv", "_active_users_timeseries.csv")
# if the input filename doesn't have ".csv" in it you might end up overwriting
# the input file with the output file and that would be bad; don't do that.
if outfile == classfile_in:
    outfile += "_active_users_timeseries.csv"

# Print out the input parameters just as a sanity check
print("File to be read: %s" % classfile_in)

print(len(sys.argv))

# check for other command-line arguments
if len(sys.argv) > 2:
    # if there are additional arguments, loop through them
    for i_arg, argstr in enumerate(sys.argv[2:]):
        arg = argstr.split('=')

        if arg[0]   == "workflow_id":
            workflow_id = int(arg[1])
            print("Restricting classifications to workflow id: %d" % workflow_id)
        elif arg[0] == "workflow_version":
            workflow_version = arg[1]
            print("Restricting classifications to workflow version: %d" % int(workflow_version))
        elif arg[0] == "outfile":
            outfile = arg[1]
        elif arg[0] == "project":
            project_name = arg[1]
        elif arg[0] == "--time_spent":
            time_spent = True
        elif arg[0] == "--days":
            dt_unit = 'D'
        elif arg[0] == "--plots_only":
            plot_only = True

print("File to be written: %s" % outfile)

if not plot_only:
    print("Reading classifications...")

    #classifications = pd.read_csv(classfile_in)
    # the above will work but uses a LOT of memory for projects with > 1 million
    # classifications. Nothing here uses the actual classification data so don't read it
    if time_spent:
        cols_keep = ["user_name", "user_id", "user_ip", "workflow_id", "workflow_version", "created_at", "metadata"]
    else:
        cols_keep = ["user_name", "user_id", "user_ip", "workflow_id", "workflow_version", "created_at"]

    classifications = pd.read_csv(classfile_in, usecols=cols_keep)

    # now restrict classifications to a particular workflow id/version if requested
    if (workflow_id > 0) | (float(workflow_version) > 0):

        # only keep the stuff that matches these workflow properties
        if (workflow_id > 0):

            #print("Considering only workflow id %d" % workflow_id)

            in_workflow = classifications.workflow_id == workflow_id
        else:
            # the workflow id wasn't specified, so just make an array of true
            in_workflow = np.array([True for q in classifications.workflow_id])

        if (workflow_version > 0):

            classifications['version_int'] = [int(q) for q in classifications.workflow_version]

            #print("Considering only major workflow version %d" % int(workflow_version))

            # we only care about the major workflow version, not the minor version
            in_version = classifications.version_int == int(workflow_version)
        else:
            in_version = np.array([True for q in classifications.workflow_version])


        if (sum(in_workflow & in_version) == 0):
            print("ERROR: your combination of workflow_id and workflow_version does not exist!\nIgnoring workflow id/version request and computing stats for ALL classifications instead.")
            #classifications = classifications_all
        else:
            # select the subset of classifications
            classifications = classifications[in_workflow & in_version]


    else:
        # just use everything
        #classifications = classifications_all

        workflow_ids = classifications.workflow_id.unique()
        # this takes too much CPU time just for a print statement. Just use float versions
        #classifications['version_int'] = [int(q) for q in classifications.workflow_version]
        version_ints = classifications.workflow_version.unique()

        print("Considering all classifications in workflow ids:")
        print(workflow_ids)
        print(" and workflow_versions:")
        print(version_ints)


    if time_spent:
        classifications['meta_json'] = [ujson.loads(q) for q in classifications.metadata]
        classifications['started_at_str']  = [q['started_at'].replace('T',' ').replace('Z', '')  for q in classifications.meta_json]
        classifications['finished_at_str'] = [q['finished_at'].replace('T',' ').replace('Z', '') for q in classifications.meta_json]

        sa_temp = classifications['started_at_str']
        fa_temp = classifications['finished_at_str']


    classifications['count'] = np.ones_like(classifications.user_name)

    print("Creating timeseries...")#,datetime.datetime.now().strftime('%H:%M:%S.%f')

    ca_temp = classifications['created_at'].copy()

    # Do these separately so you can track errors to a specific line
    # Try the format-specified ones first (because it's faster, if it works)
    try:
        classifications['created_at_ts'] = pd.to_datetime(ca_temp, format='%Y-%m-%d %H:%M:%S %Z')
    except Exception as the_error:
        #print "Oops:\n", the_error
        try:
            classifications['created_at_ts'] = pd.to_datetime(ca_temp, format='%Y-%m-%d %H:%M:%S')
        except Exception as the_error:
            #print "Oops:\n", the_error
            classifications['created_at_ts'] = pd.to_datetime(ca_temp)
            # no except for this because if it fails the program really should exit anyway

    if time_spent:
        try:
            classifications['started_at_ts'] = pd.to_datetime(sa_temp, format='%Y-%m-%d %H:%M:%S %Z')
        except Exception as the_error:
            #print "Oops:\n", the_error
            try:
                classifications['started_at_ts'] = pd.to_datetime(sa_temp, format='%Y-%m-%d %H:%M:%S')
            except Exception as the_error:
                #print "Oops:\n", the_error
                classifications['started_at_ts'] = pd.to_datetime(sa_temp)
                # no except for this because if it fails the program really should exit anyway

        try:
            classifications['finished_at_ts'] = pd.to_datetime(fa_temp, format='%Y-%m-%d %H:%M:%S %Z')
        except Exception as the_error:
            #print "Oops:\n", the_error
            try:
                classifications['finished_at_ts'] = pd.to_datetime(fa_temp, format='%Y-%m-%d %H:%M:%S')
            except Exception as the_error:
                #print "Oops:\n", the_error
                classifications['finished_at_ts'] = pd.to_datetime(fa_temp)
                # no except for this because if it fails the program really should exit anyway

        # get the length of each classification, according to metadata
        classifications['class_t_length'] = classifications.finished_at_ts - classifications.started_at_ts

        # the metadata isn't 100% reliable so flag anything that's reporting weird values
        # accept lengths between 0 < dt < 30 minutes
        # anything outside that is either a wrongly reported time or the user walked away from their computer

        classifications['class_t_length_ok'] = (classifications.class_t_length > np.timedelta64(0, 's')) & (classifications.class_t_length < np.timedelta64(30, 'm'))



    # index this into a timeseries
    # this means the index might no longer be unique, but it has many advantages
    classifications.set_index('created_at_ts', inplace=True, drop=False)

    # get the first and last classification timestamps
    first_class = min(classifications.created_at_ts)
    last_class  = max(classifications.created_at_ts)

    if dt_unit == 'D':
        time_start_str = first_class.strftime('%Y-%m-%d 00:00:00')
        time_end_str   =  last_class.strftime('%Y-%m-%d 00:00:00')
    else:
        time_start_str = first_class.strftime('%Y-%m-%d %H:00:00')
        time_end_str   =  last_class.strftime('%Y-%m-%d %H:00:00')

    time_start = pd.to_datetime(time_start_str, format='%Y-%m-%d %H:%M:%S')
    time_end   = pd.to_datetime(time_end_str,   format='%Y-%m-%d %H:%M:%S') + np.timedelta64(1, dt_unit)

    if time_spent:
        timespent_head = ",class_t_spent_sec,n_class_t_spent,n_users_t_spent"
    else:
        timespent_head = ""
    # writing to a file as we go turns out to be faster
    fout = open(outfile, "w")
    fout.write("time_start,time_end,n_class_cumul,n_class_total,n_class_registered,n_class_unregistered,n_users_total,n_users_registered,n_users_unregistered,gini_this,gini_cumul%s\n" % timespent_head)

    the_time = time_start
    # testing purposes
    #the_time = pd.to_datetime("2017-04-04 00:00:00", format='%Y-%m-%d %H:%M:%S')
    dt = np.timedelta64(1, dt_unit)
    nclass_cumul = 0

    while the_time < time_end:
        # pick just the classifications in this time period
        the_time_hi = the_time + dt
        subclass = classifications[(classifications.created_at_ts >= the_time) & (classifications.created_at_ts < the_time_hi)]

        # just the usernames
        subusers = subclass.user_name.unique()

        # total classification count
        n_class = len(subclass)

        if n_class > 0:

            # total user count
            n_users = len(subusers)

            # identify registered and unregistered users
            is_unregistered_user = np.array([q.startswith("not-logged-in") for q in subusers])
            is_registered_user   = np.invert(is_unregistered_user)
            n_users_unreg = sum(is_unregistered_user)
            n_users_reg   = n_users - n_users_unreg

            # count classifications by registered and unregistered users
            is_unregistered_class = np.array([q.startswith("not-logged-in") for q in subclass.user_name])
            is_registered_class   = np.invert(is_unregistered_class)
            n_class_unreg = sum(is_unregistered_class)
            n_class_reg   = n_class - n_class_unreg

            byuser = subclass.groupby('user_name')
            nclass_byuser = byuser['count'].aggregate('sum')
            # Gini coefficient - see the comments above the gini() function for more notes
            if n_users > 1:
                gini_this = gini(nclass_byuser)
            else:
                # if there's only 1 user then they did all the work - technically this is NaN but pick something
                gini_this = -1.0

            # get cumulative gini coefficient as well
            subclass_cumul = classifications[(classifications.created_at_ts < the_time_hi)]
            nclass_cumul   = len(subclass_cumul)
            nclass_byuser_cumul = (subclass_cumul.groupby('user_name'))['count'].aggregate('sum')
            if len(nclass_byuser_cumul) > 1:
                gini_cumul = gini(nclass_byuser_cumul)
            else:
                gini_cumul = 0.0

            if time_spent:

                nclass_tok = sum(subclass.class_t_length_ok)
                subusers_t = subclass.user_name[subclass.class_t_length_ok].unique()
                n_users_t  = len(subusers_t)

                if nclass_tok > 0:
                    t_spent_this = np.sum(subclass.class_t_length[subclass.class_t_length_ok]) / np.timedelta64(1, 's')
                else:
                    t_spent_this = 0.0

                time_spent_str = ",%.2f,%d,%d" % (t_spent_this, nclass_tok, n_users_t)
            else:
                time_spent_str = ""

            fout.write("%s,%s,%d,%d,%d,%d,%d,%d,%d,%.2f,%.2f%s\n" % (the_time.strftime('%Y-%m-%d %H:%M:%S'), the_time_hi.strftime('%Y-%m-%d %H:%M:%S'), nclass_cumul, n_class, n_class_reg, n_class_unreg, n_users, n_users_reg, n_users_unreg,gini_this,gini_cumul,time_spent_str))
        else:
            # there weren't any classifications in this time period
            # so everything is zero
            if time_spent:
                time_spent_str = ",0,0,0"
            else:
                time_spent_str = ""

            fout.write("%s,%s,%d,0,0,0,0,0,0,0,0%s\n" % (the_time.strftime('%Y-%m-%d %H:%M:%S'), the_time_hi.strftime('%Y-%m-%d %H:%M:%S'), nclass_cumul, time_spent_str))


        the_time += dt
        # end of while loop

    fout.close()

# end "if not plot_only"

# now read in the csv and make a plot or two
the_ts = pd.read_csv(outfile)
t_temp = the_ts['time_end'].copy()
the_ts['time_end_ts'] = pd.to_datetime(t_temp, format='%Y-%m-%d %H:%M:%S')

# get fraction of classifications and users that's from logged-in users
the_ts['f_class_reg'] = the_ts['n_class_registered'].astype(float) / the_ts['n_class_total'].astype(float)
the_ts['f_users_reg'] = the_ts['n_users_registered'].astype(float) / the_ts['n_users_total'].astype(float)

# estimate some error bars on the fractions of classifications and users by
# figuring out how the fractions would change if the logged-in classification/user
# count for that time period changed by a particular amount
dn_class = 25.
dn_users = 5.
the_ts['df_class_reg'] = dn_class / the_ts['n_class_total'].astype(float)
the_ts['df_users_reg'] = dn_users / the_ts['n_users_total'].astype(float)

# make sure you don't get error bars that take your fractions to < 0 or > 1
the_ts['df_class_reg_hi'] = the_ts.df_class_reg * 1.0
the_ts['df_class_reg_lo'] = the_ts.df_class_reg * 1.0
the_ts.loc[(the_ts.f_class_reg + the_ts.df_class_reg_hi > 1.), 'df_class_reg_hi'] = 1. - the_ts.f_class_reg
the_ts.loc[(the_ts.f_class_reg - the_ts.df_class_reg_lo < 0.), 'df_class_reg_lo'] = the_ts.f_class_reg

the_ts['df_users_reg_hi'] = the_ts.df_users_reg.copy()
the_ts['df_users_reg_lo'] = the_ts.df_users_reg.copy()
the_ts.loc[(the_ts.f_users_reg + the_ts.df_users_reg_hi > 1.), 'df_users_reg_hi'] = 1. - the_ts.f_users_reg
the_ts.loc[(the_ts.f_users_reg - the_ts.df_users_reg_lo < 0.), 'df_users_reg_lo'] = the_ts.f_users_reg

nonzero_class = the_ts['n_class_total'] > 0


if time_spent:
    the_ts['t_per_class'] = np.zeros_like(the_ts.class_t_spent_sec)
    the_ts['t_per_user']  = np.zeros_like(the_ts.class_t_spent_sec)
    the_ts.loc[nonzero_class, 't_per_class'] = the_ts['class_t_spent_sec'][nonzero_class] / (the_ts['n_class_t_spent'].astype(float))
    the_ts.loc[nonzero_class, 't_per_user']  = the_ts['class_t_spent_sec'][nonzero_class] / (the_ts['n_users_t_spent'].astype(float))


# figure out what the output plot filenames will be
if classfile_in.endswith('classifications.csv'):
    outplot_class = classfile_in.replace('classifications.csv', 'class-timeline.pdf')
    outplot_users = classfile_in.replace('classifications.csv', 'users-timeline.pdf')
    outplot_fracs = classfile_in.replace('classifications.csv', 'fracs-timeline.pdf')
    outplot_times = classfile_in.replace('classifications.csv', 'times-timeline.pdf')
    outplot_ginis = classfile_in.replace('classifications.csv', 'ginis-timeline.pdf')
else:
    classfile_stub = (classfile_in.split("."))[0]
    outplot_class = '%s_classifications_plot.pdf' % classfile_stub
    outplot_users = '%s_users_plot.pdf' % classfile_stub
    outplot_fracs = '%s_fractions_plot.pdf' % classfile_stub
    outplot_times = '%s_classtimes_plot.pdf' % classfile_stub
    outplot_ginis = '%s_ginis_plot.pdf' % classfile_stub

reg_color   = '#6200A2'
unreg_color = '#0E7C0E'

# format of dates on the x-axis
axisFmt = mdates.DateFormatter('%Y-%m-%d %H:%M')


################################################################################
##############################                    ##############################
#########################     Classifications Plot     #########################
##############################                    ##############################
################################################################################
gs = gridspec.GridSpec(2, 1, height_ratios=[1,2])
fig = plt.figure(figsize=(10,8))
axt = fig.add_subplot(gs[1])
axf = fig.add_subplot(gs[0], sharex=axt)

ymin = 0
ymax = max(the_ts['n_class_total'])

axt.set_ylim(ymin, ymax)

axf.fill_between(np.array(the_ts['time_end_ts']), y1=np.array(the_ts['f_class_reg']-the_ts['df_class_reg_lo']), y2=np.array(the_ts['f_class_reg']+the_ts['df_class_reg_hi']), color=reg_color, alpha=0.15, label='_nolabel_')
axf.plot(the_ts['time_end_ts'], the_ts['f_class_reg'], color=reg_color, marker='None')
axf.set_ylabel('Logged-in classification fraction', fontsize=11)

cmin = the_ts['n_class_registered']*0

#ax.plot(the_ts['time_end_ts'], the_ts['n_class_total'], marker='None', label='All classifications per hour')
#ax.plot(the_ts['time_end_ts'], the_ts['n_class_registered'],   marker='None', label='Classifications by registered users')
#ax.plot(the_ts['time_end_ts'], the_ts['n_class_unregistered'], marker='None', label='Classifications by unregistered users')

axt.fill_between(np.array(the_ts['time_end_ts']), y1=np.array(cmin), y2=np.array(the_ts['n_class_registered']), color=reg_color, alpha=0.5, label='_nolabel_')
axt.fill_between(np.array(the_ts['time_end_ts']), y1=np.array(the_ts['n_class_registered']), y2=np.array(the_ts['n_class_total']), color=unreg_color, alpha=0.3, label='Classifications by not-logged-in users')

axt.legend(frameon=False, loc=2, fontsize=11)
axt.xaxis.set_major_formatter(axisFmt)

fig.autofmt_xdate()

if len(project_name) > 0:
    plt.title(project_name)

plt.tight_layout()

plt.savefig(outplot_class, frameon=False, bbox_inches='tight', pad_inches=0.1, transparent=True)
plt.savefig(outplot_class.replace('.pdf', '.png'), frameon=False, bbox_inches='tight', pad_inches=0.1, transparent=True)
plt.close()


################################################################################
##############################                    ##############################
#########################          Users Plot          #########################
##############################                    ##############################
################################################################################

gs = gridspec.GridSpec(2, 1, height_ratios=[1,2])
fig = plt.figure(figsize=(10,8))
axt = fig.add_subplot(gs[1])
axf = fig.add_subplot(gs[0], sharex=axt)

ymin = 0
ymax = max(the_ts['n_users_total'])

axt.set_ylim(ymin, ymax)

axf.fill_between(np.array(the_ts['time_end_ts']), y1=np.array(the_ts['f_users_reg']-the_ts['df_users_reg_lo']), y2=np.array(the_ts['f_users_reg']+the_ts['df_users_reg_hi']), color=reg_color, alpha=0.15, label='_nolabel_')
axf.plot(the_ts['time_end_ts'], the_ts['f_users_reg'], color=reg_color, marker='None')
axf.set_ylabel('Logged-in user fraction', fontsize=11)


#ax.plot(the_ts['time_end_ts'], the_ts['n_users_total'],        marker='None', label='Active users per hour')
#ax.plot(the_ts['time_end_ts'], the_ts['n_users_registered'],   marker='None', label='Registered active users')
#ax.plot(the_ts['time_end_ts'], the_ts['n_users_unregistered'], marker='None', label='Unregistered active users')

axt.fill_between(np.array(the_ts['time_end_ts']), y1=np.array(cmin), y2=np.array(the_ts['n_users_registered']), color=reg_color, alpha=0.5, label='Active users (registered)')
axt.fill_between(np.array(the_ts['time_end_ts']), y1=np.array(the_ts['n_users_registered']), y2=np.array(the_ts['n_users_total']), color=unreg_color, alpha=0.3, label='Active users (unregistered)')

axt.legend(frameon=False, loc=2, fontsize=11)
axt.xaxis.set_major_formatter(axisFmt)

if len(project_name) > 0:
    plt.title(project_name)

fig.autofmt_xdate()
plt.tight_layout()


plt.savefig(outplot_users, frameon=False, bbox_inches='tight', pad_inches=0.1, transparent=True)
plt.savefig(outplot_users.replace('.pdf', '.png'), frameon=False, bbox_inches='tight', pad_inches=0.1, transparent=True)
plt.close()



################################################################################
##############################                    ##############################
#########################        Fraction Plots        #########################
##############################                    ##############################
################################################################################

class_color = '#005492'
users_color = '#C73300'

fig = plt.figure(figsize=(10,5))
axf = fig.add_subplot(1,1,1)

axf.fill_between(np.array(the_ts['time_end_ts']), y1=np.array(the_ts['f_class_reg']-the_ts['df_class_reg_lo']), y2=np.array(the_ts['f_class_reg']+the_ts['df_class_reg_hi']), color=class_color, alpha=0.15, label='_nolabel_')
axf.fill_between(np.array(the_ts['time_end_ts']), y1=np.array(the_ts['f_users_reg']-the_ts['df_users_reg_lo']), y2=np.array(the_ts['f_users_reg']+the_ts['df_users_reg_hi']), color=users_color, alpha=0.15, label='_nolabel_')


axf.plot(the_ts['time_end_ts'], the_ts['f_class_reg'], color=class_color, marker='None', label='Logged-in classification fraction')
axf.plot(the_ts['time_end_ts'], the_ts['f_users_reg'], color=users_color, marker='None', label='Logged-in user fraction')

axf.legend(frameon=False, loc='lower right', fontsize=11)
axf.xaxis.set_major_formatter(axisFmt)

if len(project_name) > 0:
    plt.title(project_name)

fig.autofmt_xdate()
plt.tight_layout()

plt.savefig(outplot_fracs, frameon=False, bbox_inches='tight', pad_inches=0.1, transparent=True)
plt.savefig(outplot_fracs.replace('.pdf', '.png'), frameon=False, bbox_inches='tight', pad_inches=0.1, transparent=True)
plt.close()


################################################################################
##############################                    ##############################
#########################          Gini Plots          #########################
##############################                    ##############################
################################################################################

class_color = '#005492'
users_color = '#C73300'

fig = plt.figure(figsize=(10,5))
axf = fig.add_subplot(1,1,1)

more_than_1_user = the_ts['n_users_total'] > 1

axf.plot(the_ts['time_end_ts'][more_than_1_user], the_ts['gini_this'][more_than_1_user], color=class_color, marker='None', label='Running Gini')
axf.plot(the_ts['time_end_ts'][nonzero_class], the_ts['gini_cumul'][nonzero_class], color=users_color, marker='None', label='Cumulative Gini')

axf.legend(frameon=False, loc='lower left', fontsize=11)
axf.xaxis.set_major_formatter(axisFmt)

if len(project_name) > 0:
    plt.title(project_name)

fig.autofmt_xdate()
plt.tight_layout()

plt.savefig(outplot_ginis, frameon=False, bbox_inches='tight', pad_inches=0.1, transparent=True)
plt.savefig(outplot_ginis.replace('.pdf', '.png'), frameon=False, bbox_inches='tight', pad_inches=0.1, transparent=True)
plt.close()



if time_spent:

    ################################################################################
    ##############################                    ##############################
    #########################          Times Plot          #########################
    ##############################                    ##############################
    ################################################################################

    gs = gridspec.GridSpec(2, 1, height_ratios=[1,2])
    fig = plt.figure(figsize=(10,8))
    axt = fig.add_subplot(gs[1])
    axf = fig.add_subplot(gs[0], sharex=axt)

    ymin = 0
    ymaxf = max(the_ts['t_per_class'][the_ts['n_class_t_spent'] > 10])
    ymaxt = max(the_ts['t_per_user'][ the_ts['n_class_t_spent'] > 10])

    axt.set_ylim(ymin, ymaxt)
    axf.set_ylim(ymin, ymaxf)

    axf.plot(the_ts['time_end_ts'][the_ts['n_class_t_spent'] > 10], the_ts['t_per_class'][the_ts['n_class_t_spent'] > 10], color=reg_color, marker='None')
    axf.set_ylabel('Average time spent per classification (s)', fontsize=11)

    axt.plot(the_ts['time_end_ts'][the_ts['n_class_t_spent'] > 10], the_ts['t_per_user'][the_ts['n_class_t_spent'] > 10], color=unreg_color, marker='None')
    axt.set_ylabel('Average time spent per user (s)', fontsize=11)




    #axt.legend(frameon=False, loc=2, fontsize=11)
    axt.xaxis.set_major_formatter(axisFmt)

    if len(project_name) > 0:
        plt.title(project_name)

    fig.autofmt_xdate()
    plt.tight_layout()


    plt.savefig(outplot_times, frameon=False, bbox_inches='tight', pad_inches=0.1, transparent=True)
    plt.savefig(outplot_times.replace('.pdf', '.png'), frameon=False, bbox_inches='tight', pad_inches=0.1, transparent=True)
    plt.close()




if time_spent:
    outplotstr = ", %s and .png" % outplot_times
else:
    outplotstr = ""


print("Figures output: %s and .png, %s and .png, %s and .png%s\n" % (outplot_class, outplot_users, outplot_fracs, outplotstr))






#end
