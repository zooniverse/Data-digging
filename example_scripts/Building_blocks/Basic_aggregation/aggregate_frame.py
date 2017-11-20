""" This script is a basic aggregation routine.  It serves as a framework that can be modified to
aggregate the flattened classification records from any project in a variety of ways, though it is
most useful for question and drawing tasks.  Transcriptions and survey tasks are better handled
with specialized scripts provided elsewhere in this repository."""

# depending on the functions and library members needed, additional modules may be required:
import csv
import sys
import json

csv.field_size_limit(sys.maxsize)

# set up the file locations (user specific) - There needs to be a input file and the aggregated
# out put file.  The input file is assumed to be sorted on the field we want to aggregate over.
location = r'C:\py\Data_digging\sorted_flattened-points.csv'
outlocation = r'C:\py\Data_digging\aggregate.csv'

# The next section can contain any functions we wish to use to analyse, modify or manipulate the
# aggregated data.  Once all the data has been collected together for a particular selection criteria
# (usually by subject), we can perform any analysis that depends only on the aggregated data for that
# selection and is independent of data aggregated for any other selection.  For example we can find the
# average of some input over the classifications for some subject image, but we can not at this point
# compare that to the average of the same field for other subjects which have not yet been aggregated.


def process_aggregation(subj, cl_counter, other_fields, aggregated_bin_1, aggregated_bin_2, aggregated_bin_3):
    # process the aggregated data for a subject.  The input variables are the function parameters and
    # the out_put can be any consistent function of those variables.  Typical processing could include
    # clustering drawing points, calculating vote fractions, applying a Bayesian pipeline, or simply
    # modifying the order or presentation format of the aggregate data.
    if cl_counter > some_limit: 
        out_put_1 = []
        out_put_2 = 0
        out_put_3 = []
        # Once the aggregated data is processed and the out_put variables defined we can
        # set up and write the aggregated and processed data to a file.  The field names can be chosen to
        # make the data as useful as possible. They must match the fieldnames in the section below - both
        # in order and spelling.
        new_row = {'subject_ids': subj, 'classifications': cl_counter,
               'Other field passed through from the classification file': other_fields,
               'agregated_bin_and_processed_field_1': out_put_1,
               'agregated_bin_and_processed_field_2': out_put_2,
               'agregated_bin_and_processed_field_3': out_put_3
               }
        writer.writerow(new_row)
        return True
    else:
        return False


# set up the output file names for the aggregated and processed data, and write the header.  The
# fieldnames and order must match the write block:
with open(outlocation, 'w', newline='') as file:
    fieldnames = ['subject_ids', 'classifications',
                  'Other field passed through from the classification file',
                  'agregated_bin_and_processed_field_1',
                  'agregated_bin_and_processed_field_2']
    writer = csv.DictWriter(file, fieldnames=fieldnames)
    writer.writeheader()

    # set up to read the flattened file
    with open(location) as f:
        r = csv.DictReader(f)

        # initialize a starting point subject and empty bins for aggregation
        subject = ''
        other_field = ''
        i = 1
        bin_1 = []  # fields can be aggregated as list or list of lists, or other
        bin_2 = 0   # Python data structures (dictionaries, sets, tuples or literals)
        bin_3 = ['' for count in range(0, 5)]  # example for a list of known length  ( here 5,
        #  such as a answer vector for a question with 5 multiple allowed answers)

        # Loop over the flattened classification records
        for row in r:
            # read a row and pullout the flattened data fields we need to aggregate, or pass through.
            new_subject = row['subject_ids']
            new_user = row['user_name']
            new_other_field = row['other field from the classification file we want to pass through']
            field_1 = json.loads(row['field_1'])  # complex fields must be loaded as json objects
            field_2 = row['field_2']
            field_3 = json.loads(row['some answer_vector'])

            # test for a change in the selector - in this case the selector is the subject
            if new_subject != subject:
                if i != 1:  # if not the first line, we have aggregated all the classifications for
                    # this subject and we can analyse the aggregated fields and output the results.
                    process_aggregation(subject, i, other_field, bin_1, bin_2, bin_3)

                # To star the next group, reset the selector, those things we need to pass through,
                # and the bins for the next aggregation.
                i = 1
                subject = new_subject
                users = {new_user}
                other_field = new_other_field  # an example of an other_field could be a image_number
                # or image_size that is tied to the subject_ids.
                bin_1 = field_1
                bin_2 = field_2
                bin_3 = field_3

            else:
                # the selector has not yet changed so we continue the aggregation:
                # First test for multiple classifications by the same user on this subject, and 
                # if we want to use a fixed number of classifications and a few subjects have 
                # more than the retirement limit (here set at 15).
                if users != users | {new_user} and i <= 15: 
                    users |= {new_user}
                    bin_1.extend(field_1)  # typical aggregation for lists such as drawing points
                    bin_2 += field_2  # typical aggregation for a field which can be summed
                    for count in range(0, len(field_3)):  # summing the elements of a answer_vector
                        bin_3[count] += field_3[count]
                    i += 1

        # catch and process the last aggregated group
        process_aggregation(subject, i, other_field, bin_1, bin_2, bin_3)
