""" This script takes a local copy of the Zooniverse Classification download file from a survey task
as input and  flattens the annotations field into a more user friendly format. Specifically it takes
the questions.csv file used to build the project and a few details known by the project builder to do
the same job as Brooke Simmons' aggregate_survey.py though in a completely different way.  This approach
needs a few more hardcode modifications but does not need any additional Python packages, nor the use
of command line parameters. I suspect it is slower but there have been no head to head tests on large
enough files for speed to matter.
Ms Simmons' code also does a partial aggregation.  This code aggregates the file by subject_species
and displays the results by vote fraction for each possible response.  The aggregated file is then
subjected to a filter that resolves most discrepancies between various volunteer's inputs. The output
is displayed broken out by columns (csv format) with one line per species and subject that survive the
filtering process."""

# this script was written in Python 3.6.2 "out of the box" and should run without any added packages.
import csv
import json
import sys
import operator
import os

csv.field_size_limit(sys.maxsize)

# File location section:
# Give full path and filenames for input and output files (these are user specific - this example
# is specific to my file structure while running this demo. The easiest way to get the full path
# and file name is to copy and paste from "Properties" (right click on the file name in file explorer.

# The classification data:
location = r'C:\py\Data_digging\example_classifications.csv'
# The questions and choices files used to set up the survey project:
question_file = r'C:\py\Survey_task\questions.csv'

# Output file names (whatever you want them to be)
out_location = r'C:\py\Data_digging\flatten_class_survey_demo.csv'  # a sort deletes this file after use
sorted_location = r'C:\py\Data_digging\flatten_class_survey_demo_sorted.csv'
aggregate_location = r'C:\py\Data_digging\flatten_class_survey_demo_aggregate.csv'
columns_location = r'C:\py\Data_digging\flatten_class_survey_demo_filtered.csv'


# Function definitions needed for any blocks in this area.
def include(class_record):
    #  define a function that returns True or False based on whether the argument record is to be
    #  included or not in the output file based on the conditional clauses.
    #  many other conditions could be set up to determine if a record is to be processed and the
    #  flattened data written to the output file (see flatten_class_frame for more options).

    if int(class_record['workflow_id']) == 4994:
        pass  # this one selects the workflow to include.
    else:
        return False
    if float(class_record['workflow_version']) >= 106.2:
        pass  # this one selects the first version of the workflow to include. Note the workflows
        #  must be compatible with the structure (task numbers) choices, and questions (they could
        #  differ in confusions, characteristics or other wording differences.)
    else:
        return False
    # otherwise :
    return True


def load_questions():
    #  This function loads the question.csv and creates a dictionary in memory with the possible responses
    with open(question_file) as qu_file:
        questdict = csv.DictReader(qu_file)
        questions_answers = {}
        translate_table = dict((ord(char), '') for char in u'!"#%\'()*+,-./:;<=>?@[\]^_`{|}~')
        for quest in questdict:
            questions_answers[quest['Question'].upper().translate(translate_table).replace(' ', '')] \
                = quest['Answers'].upper().translate(translate_table).split()
        return questions_answers


def empty(ques, resp):
    blank = []
    for q1 in range(0, len(ques)):
        blank.append([0 for r1 in resp[q1]])
    return blank


# Set up the output file structure with desired fields:
# The list of field names must include each field required in the output. The names, and order
# must be exactly the same here as in the writer statement near the end of the program. The names
# and order are arbitrary - your choice, as long as they are the same in both locations.
# Additional fields from the classification file can be added or removed as required.  The other
# flatten_class blocks could be added to this demo similarly as they are added to flatten-class_frame
# either the general utility blocks or any other blocks if the workflow has more that the one survey
# task in it. These blocks should be added before the first survey task immediately after "for task
# in annotations'.
# As code blocks are added to flatten the annotations JSON, columns need to be added to contain each
# newly split out group of data. Add each one using the format "' new_field_name'," .  Similarly fields
# can be removed from both places to reduce the file size if the information is not needed for the
# current purpose.

with open(out_location, 'w', newline='') as ou_file:
    fieldnames = ['classification_id',
                  'subject_ids',
                  'created_at',
                  'user_name',
                  'user_ip',
                  'choice',
                  'how_many',
                  'behaviours',
                  'any_young',
                  'any_horns',
                  "don't_care",
                  'subject_choices',
                  'all_choices'
                  ]
    writer = csv.DictWriter(ou_file, fieldnames=fieldnames)
    writer.writeheader()

    # this area for initializing counters, status lists and loading pick lists into memory:
    rc2 = 0
    rc1 = 0
    wc1 = 0
    #  this loads the question.csv as a dictionary we can split to get the question labels
    #  and possible responses we need to breakout the survey data.  It should produce the same
    #  question and response labels as the project builder but strange characters in the questions
    #  may need to be individually dealt with by adding them to the translation table in the function.
    q_a = load_questions()
    questions = list(q_a.keys())
    responses = list(q_a.values())

    #  open the zooniverse data file using dictreader, and load the more complex json strings
    #  as python objects using json.loads()
    with open(location) as class_file:
        classifications = csv.DictReader(class_file)
        for row in classifications:
            rc2 += 1
            # useful for debugging - set the number of record to process at a low number ~1000
            if rc2 == 150000:  # one more than the last line of zooniverse file to read if not EOF
                break
            if include(row) is True:
                rc1 += 1
                annotations = json.loads(row['annotations'])

                # reset field variables for the survey task for each new row
                choice = ''
                answer = ['' for q4 in questions]

                for task in annotations:
                    # If the workflow has additional tasks or you want to add other general utilities
                    # blocks, put them here before the survey task, so the writer block will have the
                    # all the data it needs prior to the end of the survey task block.

                    # The survey task block:
                    try:
                        #  main survey task recognized by project specific task number - in this case 'T0'
                        #  you need this to match your own project - it may be different!
                        if task['task'] == 'T0':
                            try:
                                m_s = 1
                                b = 1
                                for species in task['value']:
                                    m_s = m_s * b  # set up test for multiple species in one classification
                                    b = b * 0
                                    choice = species['choice']
                                    answer_vector = empty(questions, responses)

                                    for q in range(0, len(questions)):
                                        try:
                                            answer[q] = species['answers'][questions[q]]
                                            # prepare answer_vectors that will make aggregation easier
                                            # This section is optional but produces a data structure that
                                            # will be needed for a future aggregate_survey script.
                                            for r in range(0, len(responses[q])):
                                                if responses[q][r] == answer[q]:
                                                    answer_vector[q][r] = 1
                                        except KeyError:
                                            continue
                                    # This sets up the writer to match the field names above and the
                                    # variable names of their values. Note we write one line per
                                    # subject_choices:
                                    wc1 += 1
                                    writer.writerow({'classification_id': row['classification_id'],
                                                     'subject_ids': row['subject_ids'],
                                                     'created_at': row['created_at'],
                                                     'user_name': row['user_name'],
                                                     'user_ip': row['user_ip'],
                                                     'choice': choice,
                                                     'how_many': answer[0],
                                                     'behaviours': answer[1],
                                                     'any_young': answer[2],
                                                     'any_horns': answer[3],
                                                     "don't_care": answer[4],
                                                     'subject_choices': row['subject_ids'] + choice,
                                                     'all_choices': json.dumps([m_s, answer_vector])
                                                     })
                            except KeyError:
                                continue
                    except KeyError:
                        continue

# This area prints some basic process info and status
print(rc2, 'lines read and inspected', rc1, 'records processed and', wc1, 'lines written')


#  ____________________________________________________________________________________________________________

# This section defines a sort function. Note the last parameter is the field to sort by where fields
# are numbered starting from '0'  This prepares the file to be aggregated and is necessary for the
# old fashion aggregation routine I use. (note with pandas the aggregation would take about four
# lines and the file would not have to be sorted)


def sort_file(input_file, output_file_sorted, field):
    #  This allows a sort of the output file on a specific field.  Note this is a versatile function
    #  that could be added to any of the flatten_class_xxxx.py scripts (note it needs the import os
    #  and import operator lines added at the top of the script.
    with open(input_file, 'r') as in_file:
        in_put = csv.reader(in_file, dialect='excel')
        headers = in_put.__next__()
        sort = sorted(in_put, key=operator.itemgetter(field))

        with open(output_file_sorted, 'w', newline='') as out_file:
            write_sorted = csv.writer(out_file, delimiter=',')
            write_sorted.writerow(headers)
            sort_counter = 0
            for line in sort:
                write_sorted.writerow(line)
                sort_counter += 1
    # clean up temporary file
    try:
        os.remove(input_file)
    except:
        print('temp file not found and deleted')
    return sort_counter


print(sort_file(out_location, sorted_location, 11), 'lines sorted and written')


#  ____________________________________________________________________________________________________________

# This next section aggregates the responses for each subject-species and out puts the result
# with one line per subject-species. Vote fractions are calculated for each question-response
# and are displayed in a answer_vector format suitable for further analysis.

def cal_fraction(ques1, resp1, aggr1, tot):
    for q2 in range(0, len(ques1)):
        for r2 in range(0, len(resp1[q2])):
            aggr1[q2][r2] = int(aggr1[q2][r2] / tot[0] * 100 + .45)
    return aggr1


with open(aggregate_location, 'w', newline='') as ag_file:
    fieldnames = ['subject_ids', 'classifications', 'choice', 'aggregated_vector']
    writer = csv.DictWriter(ag_file, fieldnames=fieldnames)
    writer.writeheader()
    #  build a look-up table of classification totals by subject - this is needed for the calculation of
    #  vote_fraction.
    with open(sorted_location) as so_file:
        sorted_file = csv.DictReader(so_file)
        subject = ''
        class_totals = {}
        class_tot = 0
        rc3 = 0
        for row1 in sorted_file:
            rc3 += 1
            new_subject = row1['subject_ids']
            if new_subject != subject:
                if rc3 != 1:
                    class_totals[subject] = [class_tot, rc3]
                rc3 = 0
                subject = new_subject
                class_tot = json.loads(row1['all_choices'])[0]
            else:
                subject = new_subject
                class_tot += json.loads(row1['all_choices'])[0]
        class_totals[subject] = [class_tot, rc3]

    # The old fashion aggregation routine with the vote fraction and file write built in
    with open(sorted_location) as so_file:
        sorted_file = csv.DictReader(so_file)
        subject = ''
        subject_choices = ''
        rc4 = 0
        rc5 = 0
        aggregate = empty(questions, responses)
        class_count = 1
        choice_now = ''
        for row2 in sorted_file:
            rc4 += 1
            new_subject = row2['subject_ids']
            new_subject_choices = row2['subject_choices']
            all_choices = json.loads(row2['all_choices'])
            if new_subject_choices != subject_choices:
                if rc4 != 1:  # don't want to output the empty initial values
                    rc5 += 1
                    aggregate = cal_fraction(questions, responses, aggregate, class_totals[subject])
                    new_row = {'subject_ids': subject,
                               'classifications': class_totals[subject][0],
                               'choice': choice_now,
                               'aggregated_vector': json.dumps(aggregate)}
                    writer.writerow(new_row)
                subject = new_subject
                subject_choices = new_subject_choices
                choice_now = row2['choice']
                all_choices = json.loads(row2['all_choices'])
                class_count = all_choices[0]
                for q3 in range(0, len(questions)):
                    for r3 in range(0, len(responses[q3])):
                        aggregate[q3][r3] = all_choices[1][q3][r3]
            else:
                for que in range(0, len(questions)):
                    for res in range(0, len(responses[que])):
                        aggregate[que][res] += all_choices[1][que][res]
                class_count += all_choices[0]
                subject = new_subject
                subject_choices = new_subject_choices

        # catch the last aggregate after the end of the file is reached
        rc5 += 1
        aggregate = cal_fraction(questions, responses, aggregate, class_totals[subject])
        new_row = {'subject_ids': subject,
                   'classifications': class_totals[subject][0],
                   'choice': choice_now,
                   'aggregated_vector': json.dumps(aggregate)}
        writer.writerow(new_row)
    print(rc4, 'lines aggregated into', rc5, 'subject-choice categories')
# ___________________________________________________________________________________________________________

'''
  The next section applies a optional filter to accept a consensus by plurality or to determine if the
  result is too ambiguous to accept.  Multiple species, if they survive the filter, are output
  on separate lines.

 The details of the filter are as follows:

1)  The minimum number of classifications required retain a subject as classified : 4
            
2)  Then calculate the total v_f for a choice as the sum of the vote fractions for any number
            of that species eg 20% say there are one and 30% say there are two present
            then 50% agree that species is present
    The minimum total v_f to count any species as present : 20%
            if no species has a v-f over 20% then mark as 'species indeterminate'.
    Apply these limits then, of those that remain:
3)          If only one species is identified in any single classification for a subject,
                    and the highest total v_f exceeds the next highest total v_f by at least 45%
                            report that species as having consensus - see point 5 for calculating
                            "how many" to report.
                    otherwise report subject as 'species indeterminate'        
4)          If two or more species are identified in at least one classification for a subject,            
                    and if one species's total v_f exceeds the other by at least 45%, report
                            only that species see point 5 for calculating "how many" to report.
                    otherwise                             
                            if total v_f for each species exceeds 65% report all such species 
                            against that subject.
                    else report as 'species indeterminate, possibly multiple'
                            
            
5)  If only a single how_many bin exists for the majority species report that how_many and the  
    vote fraction for that species as the how many v_f as well.
      
    If a multiple "how many" bins exist for the majority species (count or identification errors): 
        If the lower count has a good consensus with a v_f higher than the next highest by at 
        least 45%, use the lower count and the total v_f (ie everyone saw at least that count).
        If the higher count has the larger v_f by at least 45% use the higher count and report 
        only the higher count v_f against it. 
        Oherwise the count is indeterminate by v_f - calculate the total number of animals 
        reported for all classifications done for that subject including species eliminated for
        low v_f - assume all animals reported are of the majority species type. Report the 
        fraction of all classifications that reported that number of animals for the subject
        as the v_f for this how_many.  Note this can produce errors if there is strong consensus 
        for multiple species, AND at least one of those has multiple how_many bins with no consensus
        on how many of that species exist. In this case the how_many is reported as "indeterminate 
        how_many" 
            
6)  No other filters are applied to the other questions with a simple v_f recorded.

This section out_puts the data in a columnar format vs the answer_vector approach above.  In this
case the column headings, to make the most sense for the project owner, needs to be manually chosen
and entered as list.  '''

column_headers = ['how_many', 'how_many_vf', 'Resting', 'Standing', 'Moving', 'Eating',
                  'Interacting', 'Young', 'No_Young', 'Horns', 'No_Horns', "Don't_care_yes", "Don't_care_no"]


def apply_tests(sub, cl_tot, choicevector, col_head):
    # Apply test 1 - were there enough classifications done to give any answer?
    if cl_tot[sub][0] < 4:
        generate_row(sub, cl_tot[sub], 'insufficient classifications', '',
                     col_head, ['' for rc in range(0, len(col_head))])
        return

    # Apply test 2 - are there enough votes to count any species?
    sorted_choice = sorted(choicevector, key=operator.itemgetter(1), reverse=True)
    if sorted_choice[0][1] < 20:
        generate_row(sub, cl_tot[sub], 'indeterminate choice, no consensus', '',
                     col_head, ['' for rc in range(0, len(col_head))])
        return

    if len(choicevector) > 1:
        # Apply test 3 - are all classifications single choice?
        if cl_tot[sub][0] == cl_tot[sub][1]:
            if sorted_choice[0][1] - sorted_choice[1][1] >= 45:
                generate_row(sub, cl_tot[sub], sorted_choice[0][0], sorted_choice[0][1],
                             col_head, generate_outlist(sorted_choice))
                return
            else:
                generate_row(sub, cl_tot[sub], 'indeterminate choice', '',
                             col_head, ['' for rc in range(0, len(col_head))])
                return
        # Apply test 4 - multiple choice classified, strong consensus for one choice
        else:
            if sorted_choice[0][1] - sorted_choice[1][1] >= 45:
                generate_row(sub, cl_tot[sub], sorted_choice[0][0], sorted_choice[0][1],
                             col_head, generate_outlist(sorted_choice))
                return
            else:
                # Apply test 4 - multiple choice classified, strong consensus for
                # multiple choice
                if sorted_choice[1][1] >= 65:
                    for item in sorted_choice:
                        if item[1] > 65:
                            generate_row(sub, cl_tot[sub], item[0], item[1],
                                         col_head, generate_outlist([item], True))
                    return
                else:
                    generate_row(sub, cl_tot[sub], 'indeterminate choice possibly multiple', '',
                                 col_head, ['' for rc in range(0, len(col_head))])
                    return
    else:
        generate_row(sub, cl_tot[sub], choicevector[0][0], choicevector[0][1],
                     col_head, generate_outlist(choicevector))
        return


def generate_row(subjt, cltot, choic, choic_v_f, colmns, outlist):
    new_line = {'subject_ids': subjt,
                'classifications': cltot[0],
                'choice': choic,
                'choice v_f': choic_v_f}
    for r7 in range(0, len(colmns)):
        new_line[colmns[r7]] = outlist[r7]
    writer.writerow(new_line)
    return None


def total_animals(choicevector):
    tot_animals = 0
    for r8 in range(0, len(choicevector)):
        for r9 in range(0, len(responses[0]) - 2):
            tot_animals += int(choicevector[r8][2][0][r9]) / 100 * int(responses[0][r9])
    return [int(round(tot_animals)), int(round((abs(tot_animals - int(tot_animals) - .5) + .5) * 100))]


def generate_outlist(choicevector, flg=False):
    # deal with the how many question
    # generate the bin_v_f list for the first choice in choicevector
    bin_v_f = []
    tot_v_f = 0
    for r4 in range(0, len(responses[0])):
        if choicevector[0][2][0][r4] > 0:
            bin_v_f.append((int(responses[0][r4]), choicevector[0][2][0][r4]))
            tot_v_f += int(choicevector[0][2][0][r4])
    if len(bin_v_f) > 1:  # multiple bins (ie counting errors or some misidentification occurred)
        binvf = sorted(bin_v_f, key=operator.itemgetter(1))
        if binvf[0][1] >= binvf[1][1] + 45:  # good consensus for lowest bin:
            out_list[0] = binvf[0][0]  # everyone saw at least this many animals
            out_list[1] = tot_v_f
        else:
            binvf = sorted(bin_v_f, key=operator.itemgetter(1), reverse=True)
            if binvf[0][1] >= binvf[1][1] + 45:  # strong consensus for highest bin:
                out_list[0] = binvf[0][0]
                out_list[1] = binvf[0][1]
            else:  # no strong consensus - revert to total animals reported across
                # all classifications for this subject
                if flg:  # multiple choice so total animals have a unknown split
                    out_list[0] = 'indeterminate count, multiple choice'
                    out_list[1] = ''
                else:
                    out_list[0] = total_animals(choicevector)[0]
                    out_list[1] = total_animals(choicevector)[1]
    else:
        # only one how_many bin:
        out_list[0] = bin_v_f[0][0]
        out_list[1] = bin_v_f[0][1]

    # deal with the rest of the questions
    c1 = 1
    for q5 in range(1, len(questions)):
        for r5 in range(0, len(responses[q5])):
            c1 += 1
            out_list[c1] = choicevector[0][2][q5][r5]

    # optional removes 0's for blank spaces
    # for r6 in range(0, len(out_list)):
    #     if out_list[r6] == 0:
    #         out_list[r6] = ''
    return out_list


with open(columns_location, 'w', newline='') as co_file:
    columns = ['subject_ids', 'classifications', 'choice', 'choice v_f']
    columns.extend(column_headers)
    fieldnames = columns
    writer = csv.DictWriter(co_file, fieldnames=fieldnames)
    writer.writeheader()
    with open(aggregate_location) as agg_file:
        aggregated_file = csv.DictReader(agg_file)
        out_list = ['' for rc in range(0, len(column_headers))]
        subject = ''
        choice_vector = []
        class_count = 0
        rc6 = 0
        # collect all the subject data together - again an old fashioned aggregation routine
        # with the filter applied to the pooled subject data.
        for row3 in aggregated_file:
            rc6 += 1
            vector = json.loads(row3['aggregated_vector'])
            new_subject = row3['subject_ids']
            if new_subject != subject:
                if rc6 != 1:  # don't want to look at the empty initial values
                    apply_tests(subject, class_totals, choice_vector,
                                column_headers)
                subject = new_subject
                total_v_f = 0
                for r10 in range(0, len(responses[0])):
                    total_v_f += vector[0][r10]
                choice_vector = [(row3['choice'], total_v_f, vector)]
            else:
                total_v_f = 0
                for r10 in range(0, len(responses[0])):
                    total_v_f += vector[0][r10]
                choice_vector.append((row3['choice'], total_v_f, vector))
                subject = new_subject

        # catch the last aggregate after the end of the file is reached
        apply_tests(subject, class_totals, choice_vector, column_headers)
print(rc6, 'subject-choices filtered')
# __________________________________________________________________________________________________________
