"""This script plot_data_interactive_aerobotany.py takes the output from aggregate_drawing_demo.csv
which is the clustered circle centres for the original Aerobotany project.  It plots the data points
and circles the clusters on the original subject image at the appropriate scale.  A legend and title
are added.

The source for the subject image which is used for the plot background is the actual zooniverse hosted
subject.  Using lookup_url.py, a lookup table of subject-url is created from the subject download from
the project.  This uses subject set and workflow_id to select the appropriate subjects and their urls.
We then use this lookup table keyed by subject to find the url for the zooniverse hosted image, and
used the url to download the image to our plot background.

Once the plot has been created and displayed, there are two options to save it.  One saves the plot as
a jpeg file with approximately the same resolution as the original image.  The down side to this approach
is the points and circles plotted on the image are a fixed size in the pixels of the image - zooming the
image increases the size of the point markers and circle line width, obscuring the image.

The second way to store the image is as a pickle file – sort of an interrupted python script where the
plot is put on hold.  To reactivate it, it must be loaded with a Python script that unpacks the pickled
file, essentially returning us to the point the file was put on hold.  The advantage of this approach
is the background image is the original subject image with no resolution loss and the pan and zoom widgets
of the original plot work as before.  Now if one zooms in the point size and circle line widths do not
change in on-screen pixels so the image is not obscured by large points and thick lines.
"""
import csv
import json
import sys
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
import os
from PIL import Image
import pickle
import requests

csv.field_size_limit(sys.maxsize)

# these paths and file names need to be modified for your application:
data_path = 'C:\\py\\Data_digging\\'  # Note the double slashes are required
file_name = 'aggregate_drawing_demo.csv'
data_location = data_path + file_name
subject_url = r'C:\py\AASubject\lookup_list_subject_url.csv'
save_location = 'C:\\py\\Data_digging\\Plots\\'


#  build a dictionary of subject-url pairs (executed once and held in memory)
def look_up_url(subject_file):
    with open(subject_file, 'r') as l_up_file:
        r = csv.DictReader(l_up_file)
        look_up = {}
        for row in r:
            look_up[row['subject_id']] = row['url']
        return look_up


# one of two save options, this one is a jpg file, with a scaled dpi and crop to
# retain as much resolution as possible in the smallest image file.  The os operations
# ensure the files can be recreated if they already exist.
def save_plot(subject_name, w, h):
    temp_file = 'temp.png'
    if os.path.isfile(temp_file):
        os.remove(temp_file)
    plt.savefig(temp_file, dpi=160 * im.size[0] / 795)
    file = Image.open(temp_file)
    box = (127 * w / 795, .516 * (.966 * w - h), 127 * w / 795 + w,
           .516 * (.966 * w - h) + h)
    region = file.crop(box)
    if os.path.isfile(save_location + subject_name + '.jpg'):
        os.remove(save_location + subject_name + '.jpg')
    region.save(save_location + subject_name + '.jpg')


#  The second save option is to save the plot as a pickle file.  This requires the use
#  of a script to open it later, but preserves all the plot functionality and resolution.
def save_pickles(subject_name):
    pickle_name = save_location + subject_name + '.fig.pickle'
    if os.path.isfile(pickle_name):
        os.remove(pickle_name)
    fig = plt.gca()
    pickle.dump(fig, open(pickle_name, 'wb'))


#  This function acquires the data to overlay on the image from the aggregated csv.
def get_data(subject_ids):
    with open(data_location, 'r') as data_file:
        r = csv.DictReader(data_file)
        for row in r:
            if subject_ids == row['subject_ids']:
                print('Data found')
                data = {'H_palm_clusters': json.loads(row['H_palm_clusters']),
                        'Hclusters': json.loads(row['Hclusters']), 'Hnoise': json.loads(row['Hnoise']),
                        'flowering_clusters': json.loads(row['flowering_clusters']),
                        'fclusters': json.loads(row['fclusters']), 'fnoise': json.loads(row['fnoise']),
                        'leafless_clusters': json.loads(row['leafless_clusters']),
                        'lclusters': json.loads(row['lclusters']), 'lnoise': json.loads(row['lnoise'])}
                return data
            continue
        print('Data Not found!')
        return None


#  This function calculates a suitable location for the label for each circle that is plotted,
#  so the label does not run off the top or right edge of the plot.
def location(centre, r, size):
    xlocate = centre[0] + .7 * r
    ylocate = centre[1] - .7 * r
    if xlocate >= size[0] - .035 * size[0]:
        xlocate = centre[0] - .7 * r - .030 * size[0]
    if ylocate <= .015 * size[0]:
        ylocate = centre[1] + .7 * r + .01*size[0]
    return [xlocate, ylocate]

# call the function to build the look_up dictionary
lookup = look_up_url(subject_url)

# begin a loop to input a subject and produce the plot for that subject.
while True:
    #  get the subject:
    subject = str(input('Enter a valid Subject Number:' + '\n'))
    try:
        url = lookup[subject]
        print('Subject found')
    except KeyError:
        print('Subject not found')
        flag = input('Do you want to try again? y or n' + '\n')
        if flag != 'y':
            break
        continue
    # acquire the data:
    data_points = get_data(subject)
    if data_points is None:
        flag = input('Do you want to try again? y or n' + '\n')
        if flag != 'y':
            break
        continue
    print('Requesting Image')

    # acquire the image directly from the zooniverse url for the chosen subject and create the basic plot.
    im = Image.open(requests.get(url, stream=True).raw)
    plt.axis([0.0, im.size[0], im.size[1], 0.0])
    plt.imshow(im)
    plt.title(subject + '  ' + file_name)
    ax = plt.gca()
    ax.axis('off')
    print('Acquired image')

    #  This section accumulates all the points we want to plot in both the clusters
    # and the noise points and plots them using ax.scatter for each point type.
    font = {'family': 'sans serif', 'color': 'yellow', 'weight': 'normal', 'size': 9}
    xh = []
    yh = []
    xf = []
    yf = []
    xl = []
    yl = []
    for cluster in data_points['Hclusters']:
        for point in cluster[1]:
            xh.append(point[0])
            yh.append(point[1])
    for point in data_points['Hnoise']:
        xh.append(point[0])
        yh.append(point[1])
    ax.scatter(xh, yh, s=4, c="white", marker='s', label='H. palm', alpha=1)
    for cluster in data_points['fclusters']:
        for point in cluster[1]:
            xf.append(point[0])
            yf.append(point[1])
    for point in data_points['fnoise']:
        xf.append(point[0])
        yf.append(point[1])
    ax.scatter(xf, yf, s=4, c="cyan", marker='s', label='Flowering', alpha=1)
    for cluster in data_points['lclusters']:
        for point in cluster[1]:
            xl.append(point[0])
            yl.append(point[1])
    for point in data_points['lnoise']:
        xl.append(point[0])
        yl.append(point[1])
    ax.scatter(xl, yl, s=4, c="red", marker='s', label='Leafless', alpha=1)

    # add a legend
    ax.legend(loc='upper right', bbox_to_anchor=(1.0, 0.13), fontsize='xx-small')

    # this section adds the circles for the clustered points using ax.add.artist(Circle....
    # The cluster labels are added using ax.text.
    for cluster in data_points['H_palm_clusters']:
        radius = 2 * cluster[2]  # for eps = .5 of median
        ax.add_artist(Circle((cluster[1][0], cluster[1][1]), radius, clip_on=False, zorder=10, linewidth=1,
                             edgecolor='white', facecolor=(0, 0, 0, 0)))
        text_location = location(cluster[1], radius, im.size)
        ax.text(text_location[0], text_location[1], str(cluster[0]), fontdict=font, alpha=1)
    for cluster in data_points['flowering_clusters']:
        radius = 2 * cluster[2]  # for eps = .5 of median
        ax.add_artist(Circle((cluster[1][0], cluster[1][1]), radius, clip_on=False, zorder=10, linewidth=1,
                             edgecolor='cyan', facecolor=(0, 0, 0, 0)))
        text_location = location(cluster[1], radius, im.size)
        ax.text(text_location[0], text_location[1], str(cluster[0]), fontdict=font, alpha=1)
    for cluster in data_points['leafless_clusters']:
        radius = 2 * cluster[2]  # for eps = .5 of median
        ax.add_artist(Circle((cluster[1][0], cluster[1][1]), radius, clip_on=False, zorder=10, linewidth=1,
                             edgecolor='red', facecolor=(0, 0, 0, 0)))
        text_location = location(cluster[1], radius, im.size)
        ax.text(text_location[0], text_location[1], str(cluster[0]), fontdict=font, alpha=1)
    # the two save options are the called in the lines directly below. One or the other (or both)
    # can be commented out if that option is not required.
    save_plot(subject, im.size[0], im.size[1])
    save_pickles(subject)
    # actually show the plot zoomed to full screen:
    mng = plt.get_current_fig_manager()
    mng.window.state('zoomed')
    plt.show()
    # Close the plot and move to the next subject selection when finished viewing the current plot
    plt.close()

print('Session terminated')
