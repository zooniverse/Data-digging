""" This script searches a given directory and generates a list of the pickle files in
that directory. It then uses operator inputs to find the desired subject plot to display.
Once the plot is inspected and retired the script is ready to find another.  This script
does expect all the pickle files in the directory to be plots and will not function
correctly without modification for other types of pickle file.  Such modifications
(in line 58 on) would be relatively simple for other purposes if needed."""

import matplotlib.pyplot as plt
import os
import pickle

#  This line needs tobe customized for your file structure and where your plots are:
data_location = 'C:\py\AAClass\Plots\\'

file_list = {}
# load the list of pickle files found in the directory:
i = 0
with os.scandir(data_location) as directory:
    for entry in directory:
        if entry.name[-6:] == 'pickle':
            i += 1
            file_list[i] = entry.name


# searches the file list for the first file that matches the subject_string
def search(subject_string):
    for ind, file in file_list.items():
        if subject_string in file:
            print('Subject found')
            return ind
    print('No Subject found!')
    return None


#  Enter a loop to input part or all of a subject number or step forward or backward
#  through the file list.
index = 1
while True:
    print('Enter all or part of a Subject Number (returns first match),')
    choice = input('"P" or "p" for the previous plot, or "enter" for the next:' + '\n')
    if choice.lower() == 'p':
        index -= 1
        if index < 1:
            print('no previous file')
            continue
    elif choice.lower() == '':
        index += 1
        if index > len(file_list):
            print('no next file')
            continue
    else:
        index_found = search(choice)
        if index_found is None:
            flag = input('Do you want to try again? y or n' + '\n')
            if flag != 'y':
                break
            continue
        else:
            index = index_found

    # generate the full file name for the file chosen and recreate the plot from the pickle file
    file_name = data_location + file_list[index]
    print(file_name)
    ax = pickle.load(open(file_name, 'rb'))
    mng = plt.get_current_fig_manager()
    mng.window.state('zoomed')
    #  show the plot zoomed to full screen and move to the next selection when it is closed.
    plt.show()
