import sys, os
import numpy as np, pandas as pd
import ujson, gc

##############################################
# defaults
##############################################

project_name = 'zwickys-quirky-transients'
class_file             = project_name + '-classifications.csv'
# workflow_file          = project_name + '-workflows.csv'
# workflow_contents_file = project_name + '-workflow_contents.csv'
# subject_file           = project_name + '-subjects.csv'

aggregated_file        = project_name + '-aggregated.csv'

# the workflow version is a string because it's actually 2 integers separated by a "."
# (major).(minor)
# i.e. 6.1 is NOT the same version as 6.10
# though note we only care about the major version below
workflow_id      = 8368
workflow_version = "6.16"

# do we want to write an extra file with just classification counts and usernames
# (and a random color column, for treemaps)?
counts_out = True
counts_out_file = 'class_counts_colors.csv'

verbose = True

# placeholder (right now we aren't weighting)
apply_weight = 0

# what's the minimum number of classifications a subject should have before we think 
# we might have enough information to want to rank its classification?
nclass_min = 5




#################################################################################
#################################################################################
#################################################################################


# Get the Gini coefficient - https://en.wikipedia.org/wiki/Gini_coefficient
# Typical values of the Gini for healthy Zooniverse projects (Cox et al. 2015) are
#  in the range of 0.7-0.9.

def gini(list_of_values):
    sorted_list = sorted(list_of_values)
    height, area = 0, 0
    for value in sorted_list:
        height += value
        area += height - value / 2.
    fair_area = height * len(list_of_values) / 2
    return (fair_area - area) / fair_area



#################################################################################
#################################################################################
#################################################################################


# assign a color randomly if logged in, gray otherwise
# this is for making a treemap of your project's contributors
def randcolor(user_label):
    import random
    if user_label.startswith('not-logged-in-'):
        # keep it confined to grays, i.e. R=G=B and not too bright, not too dark
        g = random.randint(25,150)
        return '#%02X%02X%02X' % (g,g,g)
        #return '#555555'
    else:
        # the lambda makes this generate a new int every time it's called, so that
        # in general R != G != B below.
        r = lambda: random.randint(0,255)
        return '#%02X%02X%02X' % (r(),r(),r())




#################################################################################
#################################################################################
#################################################################################
# This is the function that actually does the aggregating

def aggregate_class(grp):
    # translate the group to a dataframe because FML if I don't (some indexing etc is different)
    thegrp = pd.DataFrame(grp)

    # figure out what we're looping over below
    answers = thegrp.candidate_anno.unique()

    # aggregating is a matter of grouping by different answers and summing the counts/weights
    byans = thegrp.groupby('candidate_anno')
    ans_ct_tot = byans['count'].aggregate('sum')
    ans_wt_tot = byans['weight'].aggregate('sum')

    # we want fractions eventually, so we need denominators
    count_tot    = np.sum(ans_ct_tot) # we could also do len(thegrp)
    weight_tot   = np.sum(ans_wt_tot)

    # okay, now we should have a series of counts for each answer, one for weighted counts, and
    # the total votes and weighted votes for this subject.
    # now loop through the possible answers and create the raw and weighted vote fractions
    # and save the counts as well.

    # this is a list for now and we'll make it into a series and order the columns later
    class_agg = {}
    class_agg['count_unweighted'] = count_tot
    class_agg['count_weighted']   = weight_tot
    class_agg['subject_filename'] = thegrp.subject_filename.unique()[0]


    for a in answers:
        # ignore blank classifications
        if a is not None:
            # don't be that jerk who labels things with "p0" or otherwise useless internal indices.
            # Use the text of the response next to this answer choice in the project builder (but strip spaces)
            try:
                raw_frac_label  = ('p_'+a).replace(' ', '_')
                wt_frac_label   = ('p_'+a+'_weight').replace(' ', '_')
            except:
                # if we're here it's because all the classifications for this
                # subject are empty, i.e. they didn't answer the question, just
                # clicked done
                # in that case you're going to crash in a second, but at least
                # print out some information about the group before you do
                print("OOPS ")
                print(thegrp)
                print('-----------')
                print(a)
                print('+++++')
                print(ans_ct_tot,ans_wt_tot,count_tot,weight_tot)
                print('~~~~~~')
                print(answers)
                print(len(a))

            class_agg[raw_frac_label] = ans_ct_tot[a]/float(count_tot)
            class_agg[wt_frac_label]  = ans_wt_tot[a]/float(weight_tot)

    # oops, this is hard-coded - sorry to those trying to generalise
    col_order = ["p_Real", "p_Bogus", "p_Skip", "p_Real_weight", "p_Bogus_weight", "p_Skip_weight",
                 "count_unweighted", "count_weighted", "subject_filename"]

    return pd.Series(class_agg)[col_order]



#################################################################################
#################################################################################
#################################################################################








def aggregate_ztf(classfile_in=class_file, wfid=workflow_id, wfv=workflow_version, apply_weight=apply_weight, outfile=aggregated_file, counts_out=counts_out, counts_out_file=counts_out_file, nclass_min=nclass_min, verbose=True):

    if verbose:
        print("Reading classifications from %s ..." % classfile_in)

    classifications_all = pd.read_csv(classfile_in) # this step can take a few minutes for a big file

    this_workflow   = classifications_all.workflow_id == wfid
    # we only care about the major version
    this_wf_version = [int(q) == int(float(wfv)) for q in classifications_all.workflow_version]

    classifications = classifications_all[this_workflow & this_wf_version].copy()
    del classifications_all

    n_class = len(classifications)

    if verbose:
        print("... %d classifications selected from workflow %d, version %d." % (n_class, wfid, int(float(wfv))))


    # first, extract the started_at and finished_at from the annotations column
    classifications['meta_json'] = [ujson.loads(q) for q in classifications.metadata]

    classifications['started_at_str']  = [q['started_at']  for q in classifications.meta_json]
    classifications['finished_at_str'] = [q['finished_at'] for q in classifications.meta_json]

    classifications['created_day'] = [q[:10] for q in classifications.created_at]

    if verbose:
        print("Getting subject info...")

    # Get subject info into a format we can actually use
    classifications['subject_json'] = [ujson.loads(q) for q in classifications.subject_data]

    # the metadata saved with the subject is just this filename, but extract it
    classifications['subject_filename'] = [q[1]['subject_json']["%d" % q[1]['subject_ids']]['Filename'] for q in classifications['subject_ids subject_json'.split()].iterrows()]


    # Get annotation info into a format we can actually use
    # these annotations are just a single question, yay
    classifications['annotation_json'] = [ujson.loads(q) for q in classifications.annotations]
    classifications['candidate_anno'] = [q[0]['value'] for q in classifications.annotation_json]

    # possible answers (that are actually used) to the question
    # Should be Real, Bogus, Skip, but let's go with what's actually there
    answers = classifications.candidate_anno.unique()


    # create a weight parameter but set it to 1.0 for all classifications (unweighted) - may change later
    classifications['weight'] = [1.0 for q in classifications.workflow_version]
    # also create a count parameter, because at the time of writing this .aggregate('count') was sometimes off by 1
    classifications['count'] = [1 for q in classifications.workflow_version]


    # just so that we can check we're aggregating what we think we are
    last_class_time = max(classifications.created_at)[:16].replace(' ', '_').replace('T', '_').replace(':', 'h')+"m"




    ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## #
    #######################################################
    #         Apply weighting function (or don't)         #
    #######################################################
    ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## #

    classifications['seed'] = [0 for q in classifications.weight]
    classifications['is_gs'] = [0 for q in classifications.weight]

    if apply_weight > 0:

        if verbose:
            print("  Computing user weights...")
            print("Except there's nothing to do right now because we haven't written a weighting scheme")


    else:
        # just make a collated classification count array so we can print it to the screen
        by_user = classifications.groupby('user_name')
        user_exp = by_user.seed.aggregate('sum')
        user_weights = pd.DataFrame(user_exp)
        user_weights.columns = ['seed']
        #user_weights['user_label'] = user_weights.index
        user_weights['nclass_user'] = by_user['count'].aggregate('sum')
        user_weights['n_gs'] = by_user['is_gs'].aggregate('sum')
        # UNWEIGHTED
        user_weights['weight'] = [1 for q in user_exp]


    # bit of memory management
    gc.collect()



    # grab basic stats
    # also we'll use by_subject for the actual aggregation
    n_subj_tot  = len(classifications.subject_data.unique())
    by_subject = classifications.groupby('subject_ids')
    subj_class = by_subject.created_at.aggregate('count')
    all_users  = classifications.user_name.unique()
    n_user_tot = len(all_users)
    n_user_unreg = sum([q.startswith('not-logged-in-') for q in all_users])
    last_class_id = max(classifications.classification_id)

    # obviously if we didn't weight then we don't need to get stats on weights
    if apply_weight > 0:
        user_weight_mean   = np.mean(user_weights.weight)
        user_weight_median = np.median(user_weights.weight)
        user_weight_25pct  = np.percentile(user_weights.weight, 25)
        user_weight_75pct  = np.percentile(user_weights.weight, 75)
        user_weight_min    = min(user_weights.weight)
        user_weight_max    = max(user_weights.weight)

    nclass_mean   = np.mean(user_weights.nclass_user)
    nclass_median = np.median(user_weights.nclass_user)
    nclass_tot    = len(classifications)

    user_weights.sort_values(['nclass_user'], ascending=False, inplace=True)


    if verbose:

        ## ## ## ## ## ## ##             ## ## ## ## ## ## ## #
        #######################################################
        #            Print out basic project info             #
        #######################################################
        ## ## ## ## ## ## ##             ## ## ## ## ## ## ## #

        print("%d classifications from %d users, %d registered and %d unregistered.\n" % (nclass_tot, n_user_tot, n_user_tot - n_user_unreg, n_user_unreg))
        print("Mean n_class per user %.1f, median %.1f." % (nclass_mean, nclass_median))
        if apply_weight > 0:
            print("Mean user weight %.3f, median %.3f, with the middle 50 percent of users between %.3f and %.3f." % (user_weight_mean, user_weight_median, user_weight_25pct, user_weight_75pct))
            print("The min user weight is %.3f and the max user weight is %.3f.\n" % (user_weight_min, user_weight_max))
            cols_print = 'nclass_user weight'.split()
        else:
            cols_print = 'nclass_user'
        # don't make this leaderboard public unless you want to gamify your users in ways we already know
        # have unintended and sometimes negative consequences. This is just for your information.
        print("Classification leaderboard:")
        print(user_weights[cols_print].head(20))
        print("Gini coefficient for project: %.3f" % gini(user_weights['nclass_user']))



    # If you want to print out a file of classification counts per user, with colors
    # for making a treemap
    # honestly I'm not sure why you wouldn't want to print this, as it's very little
    # extra effort AND it's the only place we record the user weights
    if counts_out:
        if verbose:
            print("Printing classification counts to %s..." % counts_out_file)

        user_weights['color'] = [randcolor(q) for q in user_weights.index]
        user_weights.to_csv(counts_out_file)







    ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## #
    #######################################################
    # Aggregate classifications, unweighted and weighted  #
    #######################################################
    ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## #

    if verbose:
        print("\nAggregating classifications...\n")

    class_agg = by_subject['weight count candidate_anno subject_filename'.split()].apply(aggregate_class)
    # if p_Ans = 0.0 the function skipped those values, so replace all the NaNs with 0.0
    class_agg.fillna(value=0.0, inplace=True)



    #######################################################
    #                   Write to files                    #
    #######################################################
    #
    # add value-added columns
    #
    # let people look up the subject on Talk directly from the aggregated file
    class_agg['link'] = ['https://www.zooniverse.org/projects/rswcit/zwickys-quirky-transients/talk/subjects/'+str(q) for q in class_agg.index]

    # after we do the merges below the new indices might not be linked to the subject id, so save it explicitly
    #class_agg['subject_ids'] = [str(q) for q in class_agg.index]


    # make the list ranked by p_Real_weight
    # which is the same as p_Real if there isn't any weighting
    class_agg.sort_values(['p_Real_weight', 'count_weighted'], ascending=False, inplace=True)


    # if there are lots of unfinished subjects, make 2 versions of output file
    has_enough = class_agg['count_unweighted'] >= nclass_min

    if (len(has_enough) - sum(has_enough) > 50):
        outfile_enough = outfile.replace(".csv", "_nclassgt%.0f.csv" % nclass_min)

        # this is unlikely, but just in case
        if outfile_enough == outfile:
            outfile_enough += "_nclassgt%.0f.csv" % nclass_min

    else:
        # we don't need to write a second file
        outfile_enough = ''            


    if verbose:
        print("Writing aggregated output for %d subjects to file %s...\n" % (len(class_agg), outfile))
        if len(outfile_enough) > 2:
            print("   and aggregated %d subjects with n_class > %.0f to %s.\n" % (sum(has_enough), nclass_min, outfile_enough))


    if apply_weight > 0:
        pd.DataFrame(class_agg).to_csv(outfile)

        if len(outfile_enough) > 2:
            pd.DataFrame(class_agg[has_enough]).to_csv(outfile_enough)

        cols_out = class_agg.columns


    else: 

        # ignore the weighted columns
        cols_out = []
        for col in class_agg.columns:
            if (not col.endswith('_weight')) & (not col.endswith('_weighted')):
                cols_out.append(col)

        pd.DataFrame(class_agg[cols_out]).to_csv(outfile)

        if len(outfile_enough) > 2:
            pd.DataFrame(class_agg[cols_out][has_enough]).to_csv(outfile_enough)



    return pd.DataFrame(class_agg[cols_out])






if __name__ == '__main__':



    # file with raw classifications (csv)

    try:
        classfile_in = sys.argv[1]
    except:
        print("\nUsage: %s classifications_infile" % sys.argv[0])
        print("      classifications_infile is a Zooniverse (Panoptes) classifications data export CSV.\n")
        print("  Optional inputs:")
        print("    workflow_id=N")
        print("    workflow_version=N")
        print("    apply_weight=N  (0 for unweighted, or omit)")
        print("    outfile=aggregated_outfile.csv")
        print("    nclass_min=N  (default 5)")
        print("    counts_out_file=file_with_user_class_counts_and_weights.csv")
        print("    --verbose OR --silent")


    counts_out = False
    # check for other command-line arguments
    if len(sys.argv) > 2:
        # if there are additional arguments, loop through them
        for i_arg, argstr in enumerate(sys.argv[2:]):
            arg = argstr.split('=')

            if (arg[0]   == "workflow_id") | (arg[0] == "wfid"):
                workflow_id = int(arg[1])
            elif (arg[0] == "workflow_version") | (arg[0] == "wfv"):
                workflow_version = float(arg[1])
            elif (arg[0] == "outfile_csv") | (arg[0] == "outfile"):
                aggregated_file = arg[1]
            elif (arg[0] == "apply_weight") | (arg[0] == "weight"):
                apply_weight = int(arg[1])
            elif (arg[0] == "nclass_min"):
                nclass_min = int(arg[1])
            elif (arg[0] == "counts_out_file"):
                counts_out_file = arg[1]
                counts_out = True
            elif arg[0] == "--silent":
                verbose = False
            elif arg[0] == "--verbose":
                verbose = True

   

    class_agg = aggregate_ztf(classfile_in=classfile_in, wfid=workflow_id, wfv=workflow_version, apply_weight=apply_weight, outfile=aggregated_file, counts_out=counts_out, counts_out_file=counts_out_file, verbose=verbose)









# end
