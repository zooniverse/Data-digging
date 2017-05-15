import sys, os, glob
import pandas as pd, numpy as np
import ujson
import datetime
from get_workflow_info import get_workflow_info, translate_non_alphanumerics, get_short_slug


################################################################################

#    Jailbreak question annotations from their JSON
#    (will partially jailbreak markings etc, but not fully)

################################################################################

def breakout_anno_q(row, workflow_info):
    # if you're doing this by iterating yourself and feeding it a row it needs
    # to be row[1]['anno_json'] because row[0] is the row index
    # but if you're calling this by a .apply(lambda ) it doesn't have that
    # because obviously why would you want them to have the same syntax why why why
    annotations = row['anno_json']

    # I was trying this with numpy in hopes of saving time but that can lead to ordering problems
    # just saving it here in case I ever change my mind
    #
    # theclass = np.empty(len(d_cols), dtype=object)
    # the_cols = np.empty(len(d_cols), dtype=object)
    #
    # for thistask in annotations:
    #
    #     the_cols[d_cols[workflow_info[thistask['task']+'_shorttext']]] = workflow_info[thistask['task']+'_shorttext']
    #
    #     try:
    #         theclass[d_cols[workflow_info[thistask['task']+'_shorttext']]] = thistask['value']
    #     except:
    #         # in case numpy doesn't want to accept a dict for the drawing task?
    #         theclass[d_cols[workflow_info[thistask['task']+'_shorttext']]] = str(thistask['value'])


    theclass = {}
    for task in annotations:
        try:
            theclass[workflow_info[task['task']+'_shorttext']] = task['value']
        except:
            theclass[workflow_info[task['task']+'_shorttext']] = str(task['value'])

    # if things are going very badly, uncomment these and pipe the output to a logfile
    # print("------------------------------------------------------------")
    # print(row)
    # print(theclass)
    # print(pd.Series(theclass))
    # print("------------------------------------------------------------")

    return pd.Series(theclass)



################################################################################

#    Jailbreak survey annotations from their JSON

################################################################################
def breakout_anno_survey(row, workflow_info, fp, classcols, thecols):
    annotations = row['anno_json']
    #classcols = "classification_id created_at user_name user_id user_ip".split()
    printcols = classcols + thecols

    n_marks = 0
    theclass = {}

    # fill the row with the basic classification information
    # theclass['classification_id'] = row.index
    # for col in "created_at user_name user_id user_ip".split():
    #     theclass[col] = row[col]
    # actually, let's assume we haven't set classification_id to be the index
    for col in classcols:
        theclass[col] = row[col]

    # create all the other relevant columns
    for col in thecols:
        theclass[col] = ''


    for task in annotations:
        taskname = task['task']
        tasktype = workflow_info[taskname]['type']

        # for a survey we expect a survey task and a "shortcut" for e.g.
        # "Nothing Here", and they require different approaches
        # either way we'll write 1 row per mark to the file

        if tasktype == "survey":
            marks = task['value']
            for mark in marks:
                n_marks += 1

                # empty the dict of marks
                for col in thecols:
                    theclass[col] = ''

                # fill in the dict
                theclass[taskname.lower()+'_choice'] = mark['choice']
                for ans in mark['answers'].keys():
                    thelabel = workflow_info[taskname]['questions'][ans]['label_slug']
                    #thelabel = get_short_slug(ans)
                    theclass[taskname.lower()+'_'+thelabel] = mark['answers'][ans]
                # not currently doing anything with "filters"

                # print the mark
                write_class_row(fp, theclass, printcols)

        elif tasktype == "shortcut":

            n_marks += 1

            # empty the dict of marks
            for col in thecols:
                theclass[col] = ''

            # populate a default value for all the relevant columns
            for ans in workflow_info[taskname]['answers']:
                theclass[ans['label_slug']] = False

            # now populate the ones we have actual info for
            for ans_orig in task['value']:
                # get the index in the workflow answer map so we can fetch
                # the correct column label
                i_a = workflow_info[taskname]['answer_map'][ans_orig]
                ans = workflow_info[taskname]['answers'][i_a]['label_slug']
                #ans = get_short_slug(ans_orig.lower())
                theclass[ans] = True

            # now write the row to the file
            write_class_row(fp, theclass, printcols)

    return n_marks


################################################################################

#    Write a dictionary to a csv using columns and order in thecols

################################################################################

def write_class_row(fp, theclass, thecols):
    # print the row
    for i in range(len(thecols)):
        entry = theclass[thecols[i]]
        if not i == 0:
            fp.write(",")
        try:
            if isinstance(entry, (list, tuple)):
                fp.write('"%s"' % str(entry))
            else:
                fp.write(str(entry))
        except:
            pass
    fp.write("\n")

    return




################################################################################

#    Compute a vote fraction

################################################################################

def getfrac(row, colname, colcount):
    try:
        return float(row[colname])/float(row[colcount])
    except:
        return 0.0





################################################################################

#    Aggregate question vote fractions based on a dictionary of tasks

################################################################################

def aggregate_questions(classifications, theqdict, verbose=True):

    by_subj    = classifications.groupby(['subject_ids'])
    subj_ans   = by_subj['count'].aggregate('sum')
    subj_ans.name = 'n_class_total'

    # this should set up with the index==subject_ids and the column name we've just specified
    class_counts = pd.DataFrame(subj_ans)

    # .items() is python 3, .iteritems() is python 2
    for t, q in theqdict.iteritems():
        if verbose:
            print("Aggregating task %s (%s)... %s" % (t, q, datetime.datetime.now().strftime('%H:%M:%S')))

        colstem = t.lower()+'_'+q+'_'
        answers = classifications[q].unique()
        by_q_subj  = classifications.groupby(['subject_ids', q])
        q_subj_ans = by_q_subj['count'].aggregate('sum')
        subj_anscounts_df = pd.DataFrame(q_subj_ans).unstack().fillna(0.0)
        # the above ends up with multi-level column names, so let's fix that
        newcolnames  = []
        fraccolnames = []
        for namepair in subj_anscounts_df.columns:
            # [0] should be 'count' because that's the column we summmed on
            # [1] is the text of each answer
            # let's make it label-friendly
            thisans = (translate_non_alphanumerics(namepair[1], translate_to=u'')).replace('\n', '_').replace(' ', '_').replace('__', '_').replace('__', '_').lower()

            # e.g. 't1_spiral_arms_attached_yes_count'
            thisnewcol  = colstem + thisans + '_count'
            thisnewfrac = colstem + thisans + '_frac'
            newcolnames.append(thisnewcol)
            fraccolnames.append(thisnewfrac)

            class_counts[thisnewcol] = np.zeros_like(class_counts.n_class_total)


        subj_anscounts_df.columns = newcolnames
        class_counts[newcolnames] = subj_anscounts_df
        class_counts[colstem+'count'] = class_counts[newcolnames].apply(lambda row: sum(row), axis=1)

        for i, thecol in enumerate(newcolnames):
            thefraccol = fraccolnames[i]
            class_counts[thefraccol] = class_counts.apply(lambda row: getfrac(row, thecol, colstem+'count'), axis=1)

    # just some cleanup (replace NaNs with 0.0)
    class_counts.fillna(0.0, inplace=True)

    return class_counts
