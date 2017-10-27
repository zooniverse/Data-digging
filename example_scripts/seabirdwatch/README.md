# Seabirdwatch scripts
This folder contains the scripts used to during BBC's AutumnWatch (2017) to analyze the data from the point reducer set up in caesar.

This code uses python 3 and the `panoptes_aggregation` package found here: https://github.com/zooniverse/aggregation-for-caesar/

## Files needed
1. subject data dump (from the data export screen on the project's lab page)
2. reducer data dump from caesar (https://caesar.zooniverse.org/workflows/251/data_requests)
This link will require you to sign in first

## The scripts and files
There are four scripts provided and one data file.

### `seabird_data_subject_times.csv`
This is a data file that matches up the original subject file names with the dates they were taken.

### `bird_count.py`
This should be the first script that is run since it will create the data files needed by the other three scripts.

Edit lines 8 and 9 to match where the subjects export and reducer export data files are being kept.

Edit lines 12 through 14 to edit where the output files from this script are written.

The output files are:
1. `subjects_with_marks.csv`: a file with the subject ID, subject url, and site ID for each subject with at least one mark found.
2. `all_birds_over_time.csv`: This file contains the site ID, date, original file name, and point counts for each subjects with at least one bird identified.
3. `bird_count.txt`: a text file containing the classification count, dark count, and bird counts for each site ID.

### `plot_points.py`
This file will read in the reduced data file and the `subjects_with_marks.csv` file and plot the original images with the identified points for all subjects with more than 10 classifications.

Edit lines 9 and 10 to point to where these files are kept.

Edit line 72 to change the classification threshold.

Edit line 90 to point to what folder you want the images saved to.

### `sites_over_time_bins.py`
This file will create plots showing the number of identified birds over time for each site.  The current code with bin the counts by day before plotting.

Edit line 5 to point to where `all_birds_over_time.csv` is kept.

Edit line 14 to change the binning.  See the `animate_birds.py` file (line 21) to see an example of binning by week.

### `animate_birds.py`
This will create an animated bar graph of the bird counts over time for the `SKEL` site.  This code requires `ffmpeg` to be installed in order to save the movie.

Edit line 9 to point to where `all_birds_over_time.csv` is kept.

Edit line 10 to change the binning from `day` to `week``.

Edit line 11 to change the number of `tween_frames` to result in smoother animation of the bars (this was more of a test than anything else and in the end did not help much).

Edit line 12 to change the interval (in ms) between frames of the animation.

Edit line 89 to change the save path of the animation.
