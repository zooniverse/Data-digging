# This section defines a sort function. Note the last parameter is the field to sort by where fields
# are numbered starting from '0'  This prepares the file to be aggregated and is necessary for the
# old fashion aggregation routine I use. (note with pandas the aggregation would take about four
# lines and the file would not have to be sorted)

import csv
import operator


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
    # try:
    #     os.remove(input_file)
    # except:
    #     print('temp file not found and deleted')
    return sort_counter


print(sort_file(r'C:\py\Data_digging\flatten_class_drawing_demo.csv',
                r'C:\py\Data_digging\sorted_flattened-points_demo.csv', 1), 'lines sorted and written')
