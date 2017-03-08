import sys, os, json
import pandas as pd


'''
extracts a specific workflow with id workflow_id and version number workflow_version
from a dataframe workflow_df that's read from a workflows file (*not* a workflow
contents file). The workflows file is exportable from the Data Exports page in
the Project Builder.

The purpose of extracting a workflow is to figure out what structure the annotations
json will have in the classifications exports.

The workflow ID and current workflow version should appear in the project builder
on the page for that workflow. The workflow_version should be only the major version,
i.e. an integer.

Returns a dict containing information about the workflow structure, which is used
to create aggregated classifications for the project.

Example: if I want to extract workflow information from the Flying HI project for
the beta workflow (id 3590), version 12.33, I would first read in the workflows file
in a Python/iPython window or in another script with:

workflow_df = pd.read_csv('flying-hi-workflows.csv')

then, to run this and get the output, I'd call:

workflow_info = get_workflow_info(workflow_df, 3590, 12)

There is only 1 task in that workflow, with 3 drawing tools and a text sub-task
so workflow_info looks like:

In [170]: workflow_info
Out[170]:
{'n_tasks': 1,
 'tasknames': ['T0'],
 'T0_type': 'drawing',
 'T0_ntools': 3,
 'T0_tool0_type': 'point',
 'T0_tool0_ndetails': 0,
 'T0_tool1_type': 'line',
 'T0_tool1_ndetails': 0,
 'T0_tool2_type': 'ellipse',
 'T0_tool2_ndetails': 1,
 'T0_tool2_detail0_type': 'text'}

where I've sorted this so it's easier to read (it's not usually in a helpful order).

'''


def get_workflow_info(workflow_df, workflow_id, workflow_version):

    # initialize the output
    workflow_info = {}

    # parse the tasks column as a json so we can work with it (it just loads as a string)
    workflow_df['tasks_json'] = [json.loads(q) for q in workflow_df['tasks']]

    # identify the row of the workflow dataframe we want to extract
    is_theworkflow = (workflow_df['workflow_id'] == workflow_id) & (workflow_df['version'] == workflow_version)

    # extract it
    theworkflow = workflow_df[is_theworkflow]

    # pandas is a little weird about accessing stuff sometimes
    # we should only have 1 row in theworkflow but the row index will be retained
    # from the full workflow_df, so we need to figure out what it is
    i_wf = theworkflow.index[0]

    # extract the tasks as a json
    tasks = theworkflow['tasks_json'][i_wf]

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

            # for these purposes we're not going to retain the flow of tasks
            # or worry about either the question or answer text (it's not
            # contained in the workflows file anyway). We just care about
            # how many possible answers there are, so we know how to extract
            # them from each classification later.
            n_answers = len(tasks[task]['answers'])
            workflow_info[task+'_nanswers'] = n_answers


        # Drawing task
        elif task_type == 'drawing':
            # get the tools that are in this task
            these_tools = tasks[task]['tools']

            # report back the count of tools there are in the task
            n_tools = len(these_tools)
            workflow_info[task+'_ntools'] = n_tools

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

        # now that we've looped through all tasks, save the list of task names too
        workflow_info['tasknames'] = tasknames


    return workflow_info





#
