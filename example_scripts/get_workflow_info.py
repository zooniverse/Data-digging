import sys, os, ujson
import pandas as pd


'''
extracts a specific workflow with id workflow_id and version number workflow_version
from a dataframe workflow_df that's read from a workflows file, with accompanying
workflow_cont_df that's read from a workflow contents file.

The needed workflow files are exportable from the Data Exports page in the Project Builder.

The purpose of extracting a workflow is to figure out what structure the annotations
json will have in the classifications exports.

The workflow ID and current workflow version should appear in the project builder
on the page for that workflow. The workflow_version should be the full version, which
is stored as a decimal, even though it's really two integers concatenated with a .
(the major and minor versions of a workflow increment independently of one another).

Returns a dict containing information about the workflow structure, which is used
to create aggregated classifications for the project.

Example: if I want to extract workflow information from the Flying HI project for
the beta workflow (id 3590), version 12.33, I would first read in the workflow info
in a Python/iPython window or in another script with:

workflow_df  = pd.read_csv('flying-hi-workflows.csv')
workflow_cdf = pd.read_csv('flying-hi-workflow_contents.csv')

then, to run this and get the output, I'd call:

workflow_info = get_workflow_info(workflow_df, workflow_cdf, 3590, 12.33)

There is only 1 task in that workflow, with 3 drawing tools and a text sub-task
so workflow_info looks like:

In [170]: workflow_info
Out[170]:
{'n_tasks': 1,
 'tasknames': ['T0'],
 'T0_fulltext': u'Mark any features you see. \n\nUse the "Need some help" button below to see more information.\n\nIf the image is featureless, just click "Done".',
 'T0_shorttext': u'mark_any_feature___just_click_done',
 'T0_type': 'drawing',
 'T0_ntools': 3,
 'T0_tool0_type': 'point',
 'T0_tool0_ndetails': 0,
 'T0_tool1_type': 'line',
 'T0_tool1_ndetails': 0,
 'T0_tool2_type': 'ellipse',
 'T0_tool2_ndetails': 1,
 'T0_tool2_detail0_type': 'text'}

where I've sorted this so it's easier to read (the returned dict isn't sorted).

Note, the shorttext is a compression of the full question text, with punctuation
stripped and spaces replaced with underscores. It's a guess at what you might like
the headers of your aggregated data export columns to contain, but it's often a
terrible guess (task description text often starts or ends with a general direction
to click the help button or classify the central object in the image, for example,
and this sometimes ends up grabbing that), so feel free to replace it with
something that better describes the task.

'''

def get_workflow_info(workflow_df, workflow_cont_df, workflow_id, workflow_version):
    # initialize the output
    workflow_info = {}


    # max length of a question label below
    global maxlength
    maxlength = 35

    # get the major and minor workflow versions
    wfstr = (str(workflow_version)).split('.')
    wf_major = int(wfstr[0])
    try:
        wf_minor = int(wfstr[1])
    except:
        # you'll be here if only the major workflow version was supplied.
        # In that case just use the most recent minor version for this major version
        wf_minor_all = np.max(workflow_cont_df['version'][workflow_cont_df['workflow_id'] == workflow_id].unique())

    # parse the tasks column as a json so we can work with it (it just loads as a string)
    workflow_df['tasks_json']        = [ujson.loads(q) for q in workflow_df['tasks']]
    workflow_cont_df['strings_json'] = [ujson.loads(q) for q in workflow_cont_df['strings']]

    # identify the row of the workflow dataframe we want to extract
    is_theworkflow  =      (workflow_df['workflow_id'] == workflow_id) &      (workflow_df['version'] == wf_major)
    is_ctheworkflow = (workflow_cont_df['workflow_id'] == workflow_id) & (workflow_cont_df['version'] == wf_minor)

    # extract it
    theworkflow  =      workflow_df[is_theworkflow]
    ctheworkflow = workflow_cont_df[is_ctheworkflow]

    # pandas is a little weird about accessing stuff sometimes
    # we should only have 1 row in theworkflow but the row index will be retained
    # from the full workflow_df, so we need to figure out what it is
    i_wf  =  theworkflow.index[0]
    i_cwf = ctheworkflow.index[0]

    # extract the tasks as a json
    tasks   = theworkflow['tasks_json'][i_wf]
    strings = ctheworkflow['strings_json'][i_cwf]

    workflow_info = tasks.copy()

    tasknames = workflow_info.keys()
    workflow_info['tasknames'] = tasknames

    # now that we've extracted the actual task names, add the first task
    workflow_info['first_task'] = theworkflow['first_task'].values[0]

    # now join workflow structure to workflow label content for each task

    for task in tasknames:

        taskslug = get_short_slug(task.lower())

        # we don't need the help text and it just clutters things/takes up memory
        try:
            workflow_info[task]['help'] = ''
        except:
            pass

        ################
        # question task
        ################
        if (workflow_info[task]['type'] == 'single') | (workflow_info[task]['type'] == 'multiple'):

            # first, the question text for the task
            q_label = strings[workflow_info[task]['question']]
            q_slug  = get_short_slug(q_label.lower())
            workflow_info[task]['question'] = q_label
            # now make a slug for it
            workflow_info[task]['question_slug'] = "%s_%s" % (taskslug, q_slug)

            # now, do the same for each of the answers
            for i, ans in enumerate(workflow_info[task]['answers']):
                a_label = strings[workflow_info[task]['answers'][i]['label']]
                workflow_info[task]['answers'][i]['label'] = a_label
                workflow_info[task]['answers'][i]['label_slug'] = "%s_%s_a%d_%s" % (taskslug, q_slug, i, get_short_slug(a_label.lower()))


        ################
        # drawing task
        ################
        if (workflow_info[task]['type'] == 'drawing'):

            # first, the instruction text for the task
            # analogous to ['question'] for question tasks above
            q_label = strings[workflow_info[task]['instruction']]
            q_slug  = get_short_slug(q_label.lower())

            workflow_info[task]['instruction'] = q_label
            # now make a slug for it
            workflow_info[task]['instruction_slug'] = "%s_%s" % (taskslug, q_slug)

            # now, do the same for each of the drawing tools
            for i, ans in enumerate(workflow_info[task]['tools']):
                a_label = strings[workflow_info[task]['tools'][i]['label']]
                workflow_info[task]['tools'][i]['label'] = a_label
                workflow_info[task]['tools'][i]['label_slug'] = "%s_%s_a%d_%s" % (taskslug, q_slug, i, get_short_slug(a_label.lower()))


        ################
        # survey task
        ################
        if (workflow_info[task]['type'] == 'survey'):
            # yay

            # deal with the survey choices (e.g. species)
            workflow_info[task]['choices_slug'] = [taskslug + '_' + get_short_slug(x.lower()) for x in workflow_info[task]['choicesOrder']]
            for i_c, choice in enumerate(workflow_info[task]['choices'].keys()):
                c_label = strings[workflow_info[task]['choices'][choice]['label']]
                workflow_info[task]['choices'][choice]['label'] = c_label
                workflow_info[task]['choices'][choice]['label_slug'] = "%s_%s" % (taskslug, get_short_slug(choice).lower())

            # deal with the questions attached to every survey choice
            # e.g. "is [this species] moving, standing, or sleeping?"
            # because these will always be attached to a species, keep the
            # slugs short and don't repeat the taskname in them
            for i_q, q in enumerate(workflow_info[task]['questions'].keys()):
                q_key = get_short_slug(q.lower())
                q_label = strings[workflow_info[task]['questions'][q]['label']]
                workflow_info[task]['questions'][q]['label'] = q_label
                # now make a slug for it
                q_slug = get_short_slug(q_label.lower())
                workflow_info[task]['questions'][q]['label_slug'] = q_slug

                # each question has a set of possible answers (loop through them in order)
                for i_a, a in enumerate(workflow_info[task]['questions'][q]['answersOrder']):
                    a_label = strings[workflow_info[task]['questions'][q]['answers'][a]['label']]
                    workflow_info[task]['questions'][q]['answers'][a]['label'] = a_label
                    workflow_info[task]['questions'][q]['answers'][a]['label_slug'] = "%s_a%d_%s" % (q_key, i_a, get_short_slug(a_label.lower()))



        ################
        # shortcut (tickbox) task
        ################
        if (workflow_info[task]['type'] == 'shortcut'):
            # the annotations return the label but not the index or key of the answer
            # so make a map
            workflow_info[task]['answer_map'] = {}
            for i_a, ans in enumerate(workflow_info[task]['answers']):
                a_label = strings[workflow_info[task]['answers'][i_a]['label']]
                workflow_info[task]['answers'][i_a]['label'] = a_label
                workflow_info[task]['answer_map'][a_label] = i_a
                workflow_info[task]['answers'][i_a]['label_slug'] = "%s_a%d_%s" % (taskslug, i_a, get_short_slug(a_label.lower()))


    return workflow_info





# a handful of old scripts will use this format, but most will use the new format
def get_workflow_info_old(workflow_df, workflow_cont_df, workflow_id, workflow_version):

    # initialize the output
    workflow_info = {}


    # max length of a question label below
    maxlength = 35

    # get the major and minor workflow versions
    wfstr = (str(workflow_version)).split('.')
    wf_major = int(wfstr[0])
    try:
        wf_minor = int(wfstr[1])
    except:
        # you'll be here if only the major workflow version was supplied.
        # In that case just use the most recent minor version for this major version
        wf_minor_all = np.max(workflow_cont_df['version'][workflow_cont_df['workflow_id'] == workflow_id].unique())

    # parse the tasks column as a json so we can work with it (it just loads as a string)
    workflow_df['tasks_json']        = [ujson.loads(q) for q in workflow_df['tasks']]
    workflow_cont_df['strings_json'] = [ujson.loads(q) for q in workflow_cont_df['strings']]

    # identify the row of the workflow dataframe we want to extract
    is_theworkflow  =      (workflow_df['workflow_id'] == workflow_id) &      (workflow_df['version'] == wf_major)
    is_ctheworkflow = (workflow_cont_df['workflow_id'] == workflow_id) & (workflow_cont_df['version'] == wf_minor)

    # extract it
    theworkflow  =      workflow_df[is_theworkflow]
    ctheworkflow = workflow_cont_df[is_ctheworkflow]

    # pandas is a little weird about accessing stuff sometimes
    # we should only have 1 row in theworkflow but the row index will be retained
    # from the full workflow_df, so we need to figure out what it is
    i_wf  =  theworkflow.index[0]
    i_cwf = ctheworkflow.index[0]

    # extract the tasks as a json
    tasks   = theworkflow['tasks_json'][i_wf]
    strings = ctheworkflow['strings_json'][i_cwf]

    # not actually sure we need this but let's do it anyway
    first_task = theworkflow['first_task'][i_wf]

    # save the task count to the output
    workflow_info['n_tasks'] = len(tasks)

    # iterate through tasks and get the info on what's being measured in the classification
    tasknames = []
    #workflow_info['tasknames'] = tasknames

    for i, task in enumerate(tasks.keys()):
        # update the list of task names
        tasknames.append(task)

        task_type = tasks[task]['type']
        workflow_info[task+'_type'] = task_type

        # there are several types of tasks, and what populates the json depends
        # on the task.
        # 'single' = a question task with a single answer choice
        # 'multiple' = a question task with multiple possible answers
        # 'drawing' = a drawing tasks with potentially multiple drawing tools
        # and there are survey and text tasks but I am not doing those yet

        # Question task
        if (task_type == 'single') | (task_type == 'multiple'):
            #print("Question task")

            # for these purposes we're not going to retain the flow of tasks. We care
            # about how many possible answers there are, so we know how to extract
            # them from each classification later.
            n_answers = len(tasks[task]['answers'])
            workflow_info[task+'_nanswers'] = n_answers

            # extract the question text
            workflow_info[task+'_fulltext'] = strings[task+'.question']
            # the doubling of .replace('__', '_') is in case there are any "\n\n\n" strings
            qr = get_short_slug(workflow_info[task+'_fulltext'])
            workflow_info[task+'_shorttext'] = qr

        # Drawing task
        elif task_type == 'drawing':
            # get the tools that are in this task
            these_tools = tasks[task]['tools']

            # report back the count of tools there are in the task
            n_tools = len(these_tools)
            workflow_info[task+'_ntools'] = n_tools

            # extract the question text
            workflow_info[task+'_fulltext'] = strings[task+'.instruction']
            qr = get_short_slug(workflow_info[task+'_fulltext'].lower())
            workflow_info[task+'_shorttext'] = qr


            # now extract the information from each tool in the task
            for j in range(n_tools):
                toolstr = '%s_tool%d' % (task, j)
                tool = these_tools[j]

                # every tool has a type, and what we do later depends on it, so report it
                # e.g. elliptical, point, polygon, etc etc.
                workflow_info[toolstr+'_type'] = tool['type']

                n_deets = len(tool['details'])
                workflow_info[toolstr+'_ndetails'] = n_deets
                # if there are further details, record those too
                # "details" = sub-tasks
                # pretty sure the details can be either free text or questions
                if n_deets > 0:
                    # writing this is making me hate subtasks
                    # there can be an arbitrary number of subtask questions
                    # and also the subtask questions can be single, multiple or text
                    for k in range(n_deets):
                        deets_str = '%s_detail%d' % (toolstr, k)
                        deets_type = tool['details'][k]['type']
                        workflow_info[deets_str+'_type'] = deets_type

                        # if it's a text sub-task there's just 1 text box and we're good

                        # if it's a question sub-task we need to add an answer count
                        if (deets_type == 'single') | (deets_type == 'multiple'):
                            workflow_info[deets_str+'_nanswers'] = len(tool['details'][k]['answers'])

        elif task_type == 'survey':
            # the workflow file contains a lot of info about the survey but I think we don't necessarily need to specify it all
            workflow_info[task+'_nquestions']   = len(tasks[task]['questions'].keys())
            workflow_info[task+'_questions']    = tasks[task]['questions'].keys()
            workflow_info[task+'_nchoices']     = len(tasks[task]['choices'].keys())
            workflow_info[task+'_choices']      = tasks[task]['choicesOrder']
            # we need the name of the task that says e.g. "nothing here"
            workflow_info[task+'_unlinkedTask'] = tasks[task]['unlinkedTask']
            # get info about which questions have multiple answers
            workflow_info[task+'_q_multiple'] = {}
            for q in tasks[task]['questions'].keys():
                workflow_info[task+'_q_multiple'][q] = tasks[task]['questions'][q]['multiple']

        elif task_type == 'shortcut':
            # don't really do anything, because this should (?) be a single checkbox
            # e.g. "Nothing here"
            workflow_info[task+'_nanswers'] = len(tasks[task]['answers'])
            acol = []
            acol_slug = []
            for ans in tasks[task]['answers']:
                acol.append(strings[ans['label']])
                qr = get_short_slug(strings[ans['label']].lower())
                acol_slug.append(qr)
            workflow_info[task+'_answers'] = acol
            workflow_info[task+'_answers_slug'] = acol_slug


        # now that we've looped through all tasks, save the list of task names too
        workflow_info['tasknames'] = tasknames


    return workflow_info



# get the names of columns to appear in the eventual aggregated classification output
#
def get_class_cols(workflow_info):
    class_cols = []
    # always store the total classification count
    class_cols.append('class_count')

    for task in workflow_info['tasknames']:

        thetask = workflow_info[task]

        ####################
        # question task
        ####################
        if (thetask['type'] == 'single') | (thetask['type'] == 'multiple'):
            # we aggregate questions into fractions so for each question task
            # we need a classifier count who answered the question,
            # classifier counts for each response, and fractions for each response
            # this is the same whether or not the question can accept multiple
            # answers in a single classification

            q_slug = thetask['question_slug']
            # add the vote count for this task
            class_cols.append("%s_count" % q_slug)

            for i, ans in enumerate(thetask['answers']):
                a_slug = thetask['answers'][i]['label_slug']
                class_cols.append("%s_count" % a_slug)
                class_cols.append("%s_frac"  % a_slug)

        ####################
        # drawing task
        ####################
        # to do

        ####################
        # survey task
        ####################
        if (thetask['type'] == 'survey'):
            # note: below, "choices" <--> "species"
            # and "questions" <--> "behavior"
            # because I'm thinking about these in terms of ecology projects
            # but in fact they're coded in Panoptes more generally than that.
            # surveys are basically an annotations matrix, with species on one
            # axis and behaviors on the other.
            # (plus the "shortcut" of e.g. "nothing here" or "fire", etc., but
            # (those are dealt with separately below)
            # If we're looking to flatten this to make it easier for research
            # teams to deal with, we need 1 column for each entry in that matrix.
            #
            # That means a lot of columns, even before trying to keep track
            # of counts *and* fractions.
            #
            # Python can handle this, but it might get unwieldy for research
            # teams, especially if many of those columns are likely to be blank.
            # For now, we just need to define them all, and then try to
            # compress later by e.g. ignoring empty columns.

            # for each species choice, define count/frac and behavior columns
            for choice in thetask['choices_slug']:
                # the choices_slug entry should already have the task name in it
                class_cols.append("%s_count" % choice)
                #class_cols.append("%s_frac"  % choice)

                for q in thetask['questionsOrder']:
                    q_slug = thetask['questions'][q]['label_slug']
                    class_cols.append("%s_%s_count" % (choice, q_slug))
                    #class_cols.append("%s_%s_frac"  % (choice, q_slug))

                    for a in thetask['questions'][q]['answersOrder']:
                        # the answer slug already has a short form of the question in it
                        a_slug = thetask['questions'][q]['answers'][a]['label_slug']
                        class_cols.append("%s_%s_count" % (choice, a_slug))
                        #class_cols.append("%s_%s_frac"  % (choice, a_slug))


        ####################
        # shortcut task
        ####################
        if (thetask['type'] == 'shortcut'):
            # This is very similar to the question task above, but there isn't
            # any question text, so just do the answers
            for i, ans in enumerate(thetask['answers']):
                a_slug = thetask['answers'][i]['label_slug']
                class_cols.append("%s_count" % a_slug)
                class_cols.append("%s_frac"  % a_slug)


    return class_cols




def translate_non_alphanumerics(to_translate, translate_to=u'_'):
    not_letters_or_digits = u'!"#%\'()*+,-./:;<=>?@[\]^_`{|}~'
    translate_table = dict((ord(char), translate_to) for char in not_letters_or_digits)
    return to_translate.translate(translate_table)


def get_short_slug(thestr):
    qq = (translate_non_alphanumerics(thestr, translate_to=u'')).replace('\n', '_').replace(' ', '_').replace('__', '_').replace('__', '_')
    if len(qq) > maxlength:
        ii = (maxlength-2)/2
        qr = qq[:ii]+'__'+qq[-ii:]
    else:
        qr = qq

    if qr.startswith('_'):
        qr = qr[1:]
    if qr.endswith('_'):
        qr = qr[:-1]

    return qr

#
