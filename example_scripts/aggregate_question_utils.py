import sys, os, glob
import pandas as pd, numpy as np
import ujson
import datetime
from get_workflow_info import get_workflow_info, translate_non_alphanumerics

def breakout_anno(row, workflow_info):
    # if you're doing this by iterating yourself and feeding it a row it needs
    # to be row[1]['anno_json'] because row[0] is the row index
    # but if you're calling this by a .apply(lambda ) it doesn't have that
    # because obviously why would you want them to have the same syntax why why why
    annotations = row['anno_json']

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
    for thistask in annotations:
        try:
            theclass[workflow_info[thistask['task']+'_shorttext']] = thistask['value']
        except:
            theclass[workflow_info[thistask['task']+'_shorttext']] = str(thistask['value'])

    # print("------------------------------------------------------------")
    # print(row)
    # print(theclass)
    # print(pd.Series(theclass))
    # print("------------------------------------------------------------")

    return pd.Series(theclass)


def getfrac(row, colname, colcount):
    try:
        return float(row[colname])/float(row[colcount])
    except:
        return 0.0




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
