## Plot overlays

A useful way of displaying aggregated drawing data is to show the drawings and/or the consensus drawing as a overlay on the original subject image as in example 4982655.jpg.  This shows the original subject image with the centre points for all the circles that the volunteers drew on it during classification.  These points were then clustered using aggregate_drawing_demo.py, and the circles in the figure show the clusters that were made, along with a summary of the number of points in each cluster.

This figure has been produced using Python and Matplotlib, a Python package for plotting.   Unfortunately to use this, one must successfully load a number of Python packages – this will not work with out-of–the-box Python.

### Python Environment and Matplotlib Installation.

It can be a pain, particularly for Windows users, to get the necessary packages installed.
Matplotlib requires a number of packages; for the full list refer to the Installation instructions at:  https://matplotlib.org/users/installing.html

Matplotlib requires a large number of dependencies:

•	Python (>= 3.4)

•	NumPy (>= 1.7.1)

•	setuptools

•	dateutil (>= 2.0)

•	pyparsing

•	libpng (>= 1.2)

•	pytz

•	FreeType (>= 2.3) (optional)

•	cycler (>= 0.10.0)

•	six

And to work with jpg files:

•	Pillow (>=2.0): for a larger selection of image file formats: JPEG, BMP, and TIFF image files;

In addition to Matplotlib I required two additional packages to retrieve images from a url.  These are 

•	requests 2.18

•	urllib3  1.22

And finally to save the plots in an interactive format with pan and zoom we need

•	pickleshare 0.7.4

Numpy is likely to give the most difficulty if you are on Windows.  Try http://www.lfd.uci.edu/~gohlke/pythonlibs/ which is Christoph Gohlke's site which is the go-to place for Windows binaries and wheels for Python packages.

Most of these will install and load with pip:

python -mpip install -U pip

python -mpip install -U matplotlib

I was on Windows 7 professional the first time I installed Matplotlib and I used the wheels from http://www.lfd.uci.edu/~gohlke/pythonlibs after many hours trying unsuccessfully to get a third party package loaders like Anaconda and Canopy and WinPython to work.

Once Matplotlib and the dependencies were loaded and working I worked through a few of the example plots at https://matplotlib.org/gallery/index.html#pyplot-examples to make sure everything was working.   

## Example scripts:

The script plot_data_interactive_aerobotany.py takes the output from aggregate_drawing_demo.csv which is the clustered circle centres for the original Aerobotany project.  It plots the data points and circles the clusters on the original subject image at the appropriate scale.  A legend and title are added.

The source for the subject image which is used for the plot background is the actual zooniverse hosted subject.  Using lookup_url.py, a lookup table of subject-url is created from the subject download from the project.  This uses subject_set_id and workflow_id to select the appropriate subjects and their urls.   We then use this lookup table keyed by subject to find the url for the zooniverse hosted image, and use the url to download the image to our plot background.

Once the plot has been created and displayed, there are two options to save it.  One saves the plot as a jpeg file with approximately the same resolution as the original image.  The down side to this approach is the points and circles plotted on the image are a fixed size in the pixels of the image - zooming the image increases the size of the point markers and circle line width, obscuring the image.

The second way to store the image is as a pickle file – sort of an interrupted python script where the plot is put on hold.  To reactivate it, it must be loaded with a Python script that unpacks the pickled file, essentially returning us to the point the file was put on hold.  The advantage of this approach is the background image is the original subject image with no resolution loss and the pan and zoom widgets of the original plot work as before.  Now if one zooms in the point size and circle line widths do not change in on-screen pixels so the image is not obscured by large points and thick lines.

To locate and display the pickle files a script pickpickles.py searches a specified directory for all the pickle files and generates list of them. It can then cycle through or search the list by subject_id or part of the subject_id.  Once it locates the desired file it reloads the plot. When that plot is retired pickpickles is ready to locate and display the next.  Peter's pickpickles.py makes it pleasant to play with pickled plots! ( Sorry, couldn't resist.)

### Files in this repository:

•	aggregate_drawing_demo.csv  - the aggregated, clustered data sample - See the Basic_aggregation repository for how this file is created.

•	lookup_url.py - pulls subject and url from the subject download by subject set and workflow_id – Can easily be modified for other uses where specific fields need to be set up in a table.

•	lookup_list_subject_url.csv – the lookup list data for subject set 7369 and workflow 3130.

•	plot_data_interactive_aerobotany.py – the plot routine customized for Aerobotany.

•	plot_data_interactive.py – the basic generic plot routine  - a starting point for other projects

•	4982655.jpg – a sample jpeg format saved plot

•	4982655.fig.pickle – a sample pickle file for the above plot.

•	pickpickles.py – a script to find and select pickled files to display using matplotlib. This file could be used to find and load any pickle file with every few modifications to how the pickle file is activated in the last few lines.


Note that lookup_url.py and pickpickles.py are actually quite general and with little modification could be used for many purposes beyond their specific use here.
