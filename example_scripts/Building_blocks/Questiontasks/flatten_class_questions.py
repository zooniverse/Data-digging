""" In the Classification download, the user's responses to each task are recorded in a field called
'annotations' (including those of experts and those tagged "TRUE" for being gold standard responses.
The field is a JSON string. When loaded into Python using the json.loads() function from import json,
it becomes a dictionary of dictionaries of form {{....}, {.....}, {....}} with a dictionary for each
task the user is required to complete, in the order completed.
The form of the individual dictionaries for the tasks depends very much on what type of task it is -
a question, drawing tool, transcription or survey task.  This set of scripts are for question tasks,
which have the form {"task":"TX", "task_label":"question the users saw", "value":"answers chosen"}.
For simple questions with one answer choice this is pretty simple, especially if one knows which of
the blocks in annotations we are dealing with. Even without that we can find the correct task because
we know the question text.  Due to the way the project builder can be assembled, it is unlikely tasks are
numbered in the order completed, and with the conditional branching allowed, tasks are not even in the
same order in every response.
The following blocks describe ways to address these issues for question tasks:"""

#  ___________________________________________________________________________________________________________

#Block 1 Question task is the first task completed, and has a single REQUIRED answer:
    # First add this block below to the body of the frame (see demos) and ensure the line
                annotations = json.loads(row['annotations']) # is not commented out
    # Second add a output field to the file-name list and writer list with value task_answer.  Note, the
    # field_name can be anything you want though often it is some snippet of the question.

                # generate First task
                first_task = annotations[0]
                task_answer = str(first_task['value'])

# Optional further processing:
# task will end up the answer text of the answer chosen. This may be unnecessarily long
# or in some cases be multi lines, or contain characters like '\n' which will cause problems later.
# In this case one can truncate the answer, slice out some section of it, or even turn it into an
# integer.  As many conditional statements as needed to massage each possible answer can
# ensure the data in the output file has the format you need for further processing or aggregation.
# Because the possible responses are limited to the texts built into the project builder this approach
# is sufficiently robust for question tasks (we are not building mission critical software here!)
# Examples:
                if task_answer.find('some text') >= 0:
                    task_answer = task_answer[2:10]  # slice out characters from certain answers
                if task_answer.find('some other text') >= 0:
                    task_answer = 10000
                # For multi choice, single answer questions eg three choices with one choice allowed, assigning
                # integers to the answers, 1 for answer choice 1, 100 for answer choice 2 and 10000 for answer
                # choice 3 allows all possible answers to be aggregated by simply summing the integers of all
                # responses - eg a sum 60702 would tell us 2 people chose answer 1, 7 chose answer 2 and 6 chose
                # answer 3. Obviously this works for up to 99 responders.
                if task_answer == 'Yes': # question required either Yes or No but not both!
                    task_answer = 1
                else:
                    task_answer = 0

#_____________________________________________________________________________________________________________________
#  Block 2  Question task is not necessarily the first task completed, and has a single answer which may not
#  be required:  Output is the actual answers, one column per question.
# In this case we do not know where or if the associated task will appear in annotations. Note this block can
# handle first questions as well.
    # First add this block below to the body of the frame  see demos and ensure the line
                annotations = json.loads(row['annotations']) #  is not commented out
    # Second add a output field(s) to the file-name list and writer list with value(s) task_answer_X.  Note, the
    # field_name can be anything you want though often it is some snippet of the question.

                task_answer_1 = ''
                task_answer_2 = ''
                #...
                task_answer_N = ''

                for task in annotations:
                    try:
                        if 'snippet of question 1' in task['task_label']:
                            if task['value'] is not None:
                                task_answer_1 = str(task['value'])
                    except KeyError:
                        continue
                    try:
                        if 'snippet of question 2' in task['task_label']:
                            if task['value'] is not None:
                                task_answer_2 = str(task['value'])
                    except KeyError:
                        continue
                    #....
                    try:
                        if 'snippet of question N' in task['task_label']:
                            if task['value'] is not None:
                                task_answer_N = str(task['value'])
                    except KeyError:
                        continue





# further optional processing of task answer as above would be inserted before the exception

#  Repeat this block with unique variable names replacing task_answer for each single answer question in
#  the workflow for which you want the answer in the output file. Assign unique field names in the list of
#  fieldnames and in the writer statement and set their values to the appropriate variable names replacing
#  task_answer.

#________________________________________________________________________________________________________________
# Multiple answer questions: While Block 2 will handle multi-answer questions, the multiple answers will be in
# a list with more than one string or value in it.  To break out multiple answers we can either accept this and
# worry about simplifying the field later, we can split the multiple answers out now into separate columns (Block 3),
# or we can generate a answer vector which contains all the information but in a simpler form than a list of
# answer texts using the verbiage from the project. One possible answer vector using integers which allow easy
# aggregation counts of each answer is presented in Block 4

# Block 3 Questions with multiple-allowed answers split out into separate columns for each possible answer.
# In the following, 'answer 1', 'answer 2' etc are snippets from each of the possible answers to a multiple-allowed
# answers question. 'snippet of multiple question n' is a snippet from a question found only in one task.  Note
# 'answer 1', 'answer 2' etc may be actually be answers for more than one question, but the task_answer_n_1,
# task_answer_n_2 etc will be specific to the question task 'n' answer 1, task 'n' answer 2, etc. For every value of
# task_answer_n_i there will be a separate column.  This become unwieldy if there are many questions and answers
# which is addressed in Block 4

    # First add this block below to the body of the frame  see demos and ensure the line
                annotations = json.loads(row['annotations']) # is not commented out
    # Second add a output field(s) to the file-name list and writer list with value(s) task_answer_x_x.  Note, the
    # field_name can be anything you want though often it is some snippet of the question. There will be one per
    # column.

                # for single answer questions as before:
                task_answer_1 = ''
                #....
                # but for multiple answer questions where we want the answers broken out their individual columns
                # each possible answer variable must be reset to ''
                task_answer_n_1 = ''
                task_answer_n_2 = ''
                task_answer_n_3 = ''
                #....

                #....
                task_answer_N = ''

                for task in annotations:
                    # for single answer questions as before:
                    try:
                        if 'snippet of question 1' in task['task_label']:
                            if task['value'] is not None:
                                task_answer_1 = str(task['value'])
                    except KeyError:
                        continue
                    # but for multiple-allowed answer questions expand the scope as follows:
                    try:
                        if 'snippet of multiple question n' in task['task_label']:
                            if 'answer 1' in task['value']:
                                task_answer_n_1 = 'answer 1' # or any other designator you desire for that response
                            elif 'answer 2' in task['value']:
                                task_answer_n_2 = 'answer 2'
                            elif 'answer 3' in task['value']:
                                task_answer_n_3 = 'answer 3'
                                #.... for as many conditions as there are possible answers
                    except KeyError:
                        continue
                    #....
                    # and more single or multiple-allowed question blocks as needed:
                    try:
                        if 'snippet of question N' in task['task_label']:
                            if task['value'] is not None:
                                task_answer_N = str(task['value'])
                    except KeyError:
                        continue

#  __________________________________________________________________________________________________________________
# It is readily apparent that setting up a separate column for every possible answer choice becomes very unwieldy.
# For any real project with more than a few questions and very limited possible answers we need a simpler method of
# recording the choices.

#  Block 4  Multiple-allowed answers output in a answer vector
# An answer vector is a ordered list of N entries each of which indexable ie the choice for each possible answer
# is in a prescribed location in the list.  Each entry in the list is a flag set to indicate one of two possible
# states for each option in the N multiple allowed answers.  In the simplest case the flags are 0 and 1 for the
# choice not selected or selected, though any two distinct values could be used. For example the answer vector
# for a question with five possible choice answers [0, 1, 0, 0, 1] could mean choices 2 and 5 were selected.

# The advantage of using answer vectors is the flags can be integers which makes aggregation very easy. The downside
# is this sort of output is distanced from the answer text and one needs to know what answer each element is
# associated with, particularly if the flags used simply 0 and 1's.

# To generate the answer vector we introduce the answer template - this is a list with one to one correspondence to
# the answer vector with each element a UNIQUE snippet of the answer choice which is found ONLY within the appropriate
# answer choice and NO WHERE ELSE in the json string for that task's values.  Based on the details of the project
# we define the answer template, then search systematically through the text of the task values for each element.
# If found in the task values we set the corresponding flag to indicate that answer was one of those chosen,
# otherwise it is left as the unselected flag
    #First we set up the answer template(s) in the initialize block (where i = 0 is defined) Using the same snippets
    # as for Block 3:
    task_answer_template_2 = ['answer 1', 'answer 2', 'answer 3', ... ]
    # Second, add a output field(s) to the file-name list and writer list with value(s) task_answer_x  Note, the
    # field_name can be anything you want though often it is some snippet of the question. There will be one
    # field name and column per multiple-allowed question.

    # Third, add this block below to the body of the frame  see demos and ensure the line
                annotations = json.loads(row['annotations']) # is not commented out.
                # reset the out put values:
                task_answer_1 = ''
                task_vector_2 = [0, 0, 0, ... ]  # elements are the "unselected" flags
                task_answer_N = ''
                for task in annotations:
                    # for single answer questions as before (returns the actual answer text which can be
                    # processed further if desired:
                    try:
                        if 'snippet of question 1' in task['task_label']:
                            if task['value'] is not None:
                                task_answer_1 = str(task['value'])
                    except KeyError:
                        continue

                    # but for multiple-allowed answers questions add blocks of the form
                    try:
                        if 'snippet of multiple question 2' in task['task_label']:
                            for i in range(0, len(task_answer_template_2)):
                                if task_answer_template_2[i] in task['value']:
                                    task_vector_2[i] = 1 # or what ever "selected" flag you chose
                            # optional test for no answers selected
                            # if task_vector_2 == [0, 0, 0, ...]:  # no answers selected
                            #     task_vector_2 = []
                    except KeyError:
                        # Optional treatment for task not completed
                        # task_vector_2 = ''
                        continue
                    #....

                    try:
                        if 'snippet of question N' in task['task_label']:
                            if task['value'] is not None:
                                task_answer_N = str(task['value'])
                    except KeyError:
                        continue
                # convert lists to JSON string format prior to writing them to file
                task_vector_2 = json.dumps(task_vector_2)
#  _________________________________________________________________________________________________________________

