# example_scripts
Tools for analysis of classification and subject data from github.com/zooniverse/Panoptes, which have been tested on projects.

Scripts in the top-level directory should work for any Panoptes project, and are sometimes used by more project-specific scripts in sub-directories.

## Where do I begin?

If you have a raw classifications export file and aren't sure where to start:
 - try the Jupyter notebooks `00 - First Look at Classifications` and `01 - Project Stats and Cleaning Classification Files`. They will step you through making use of the script `basic_classification_processing.py`.

 - Or, jump straight into using [basic_classification_processing.py](basic_classification_processing.py). You can run this from the command line or import it into your existing scripts. It will give you the basic information about your project's classifications but it can *also* clean your export of duplicate classifications, extract classifications from only specific workflows and/or from only Live-mode project dates, and save the cleaned classification file to a new file. It will also give you a file listing classification counts for each user. More information below.

Scripts in each project directory may contain code that needs to be modified to work on a different project, or that would need to be generalized to make them applicable to any project.

Both *basic_project_stats.py* and *sessions_inproj_byuser.py* were originally in the [panoptes_analysis](https://github.com/vrooje/panoptes_analysis) repo. They both can run on the classification export from Galaxy Zoo Bar Lengths, which is included in this repo. But they should run fine on any classification export, so long as you're operating in the Python environment defined by *basic_project_stats.yml* (for both scripts).

### More details on the general scripts in this directory

 - `active_users_timeseries.py` - makes a classification and user count timeseries, binned hourly, for logged-in and non-logged-in users. Outputs to files:
    - A csv file containing the timeseries
    - a plot of classifications per hour, with different shadings for logged-in and not-logged-in users (pdf and png)
    - a plot of active users per hour, with different shadings for logged-in and not-logged-in users (pdf and png)
    - a plot of the fraction of logged-in classifications and users per hour (pdf and png)

- `aggregate_question_utils.py` - utility functions for question task aggregation:
    - meant to be imported by other codes
    - breaks question annotations out of the raw "annotations" column of data export CSVs (deals with the JSON)
    - aggregates question votes into vote fractions. Can be weighted or unweighted aggregation depending on how you populate the 'count' column of the classifications dataframe you pass it.
    - example usage: see `galaxy_zoo_bar_lengths` folder.

 - `basic_classification_processing.py` - computes basic statistics from a raw classification export file. Run without any inputs to see usage details. In default mode, outputs to screen:
    - Total number of classifications
    - Total number of classifiers (registered and unregistered)
    - Stats on classifications per subject
    - Stats on classifications per user
    - Top 10 most prolific classifiers (note: for your edification only; I strongly recommend *against* publishing this)
    - Gini coefficient for classifications (more details on this in the code, as comments)
    - [optional] total human effort expended by classifiers in the project

    Run this program without any inputs to see its various options re: specifying workflow_ids, removing duplicate classifications, etc. There are enough possible variations (with the additional option to output a "cleaned" classification file) that this program is useful for filtering a full classification export into sub-files with, e.g., only the live, non-duplicate classifications for the workflow ID and version of your choice.

 - `basic_project_stats.py` - this is a command-line only version of `basic_classification_processing.py` and is no longer updated.
 
- `check_for_duplicate_marks.py` - checks the Classifications export for a workflow with point-type drawing tasks to see if there are duplicate annotations. Created in response to [PFE issue 5527](https://github.com/zooniverse/Panoptes-Front-End/issues/5527) where annotations on touchscreen devices would be incorrectly created twice.
 
 - `get_workflow_info.py` - extracts information about a given workflow from a json and returns it as a list. Details:
    - meant to be imported: `from get_workflow_info import get_workflow_info`
    - takes dataframes containing the raw contents of workflow and workflow-contents exports requested from the project builder
    - returns a list of tasks and details about each of them. Details in the initial comments of the script.

 - `make_author_list.py` - creates a markdown list of users for crediting on the team/results page. Can take ranked user list output from `basic_project_stats.py`. Run without inputs to get details.

 - `match_user_lists.py` - classification exports currently don't include `credited_name` or `display_name` fields, which each user can fill in if they'd prefer a proper name to be used to give credit. The best way to get those is to use `basic_project_stats.py` to generate a list of users you need names for, then ask the Zooniverse team (e.g. @mrniaboc). Once you receive the list back with credited/display names, it may not be in the order you were expecting and may not contain the info needed to re-order it the way you want. To match it back to whatever ranked file you prefer to use, run this program to combine the ranked file with the credited-name file and generate the input for `make_author_list.py`. If at some future date classification exports include the `credited_name` column, you won't need this.

 - `sessions_inproj_byuser.py` - computes classification and session statistics for classifiers. Run at the the command line without additional inputs to see the usage. *Output columns:*
    - *n_class:* total number of classifications by the classifier
    - *n_sessions:* total number of sessions by the classifier
    - *n_days:* number of unique days on which the classifier has classified
    - *first_day:* date of first classification (YYYY-MM-DD)
    - *last_day:* date of last classification (YYYY-MM-DD)
    - *tdiff_firstlast_hours:* time elapsed between first and last classification (hours)
    - *time_spent_classifying_total_minutes:* total time spent actually classifying, i.e. work effort (minutes)
    - *class_per_session_min:* minimum number of classifications per session
    - *class_per_session_max:* maximum number of classifications per session
    - *class_per_session_med:* median number of classifications per session
    - *class_per_session_mean:* mean number of classifications per session
    - *class_length_mean_overall:* mean length of a single classification (minutes), over all sessions
    - *class_length_median_overall:* median length of a single classification (minutes), over all sessions
    - *session_length_mean:* mean length of a session (minutes)
    - *session_length_median:* median length of a session (minutes)
    - *session_length_min:* length of shortest session (minutes)
    - *session_length_max:* length of longest session (minutes)
    - *which_session_longest:* session number of classifier's longest session (by time spent)
    - *mean_session_length_first2:* mean session length in the classifier's first 2 sessions (minutes)
    - *mean_session_length_last2:* mean session length in the classifier's last 2 sessions (minutes)
    - *mean_class_length_first2:* mean classification length in the classifier's first 2 sessions (minutes)
    - *mean_class_length_last2:* mean classification length in the classifier's last 2 sessions (minutes)
    - *class_count_session_list:* classification counts in each session, formatted as: [n_class_1; n_class_2; ...]

The mean session and classification lengths in the first 2 and last 2 sessions are only calculated if the user has classified in at least 4 sessions; otherwise the values are 0.
