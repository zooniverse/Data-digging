# example_scripts
Tools for analysis of classification and subject data from github.com/zooniverse/Panoptes, which have been tested on projects.

Scripts in the top-level directory should work for any Panoptes project (which at the moment means they do basic stats on rate of classification and so forth and ignore the actual classification content).

Scripts in each project directory may contain code that needs to be modified to work on a different project, or that would need to be generalized to make them applicable to any project.

Both *basic_project_stats.py* and *sessions_inproj_byuser.py* were originally in the [panoptes_analysis](https://github.com/vrooje/panoptes_analysis) repo. They both can run on the classification export from Galaxy Zoo Bar Lengths, which is included in this repo. But they should run fine on any classification export, so long as you're operating in the Python environment defined by *basic_project_stats.yml* (for both scripts). 

More details on the general scripts in this directory:

 - `basic_project_stats.py` - computes basic statistics from a raw classification export file. Run without any inputs to see usage details. Outputs to screen:
    - Total number of classifications
    - Total number of classifiers (registered and unregistered)
    - Stats on classifications per subject
    - Stats on classifications per user
    - Top 10 most prolific classifiers (note: for your edification only; I strongly recommend *against* publishing this)
    - Gini coefficient for classifications (more details on this in the code, as comments)

   This pays no attention to separate workflows or versions, so if you want those separated you will need to save a subset of the raw classification exports to a new csv file with the same format.

 - `get_workflow_info.py` - extracts information about a given workflow from a json and returns it as a list. Details:
    - meant to be imported: `from get_workflow_info import get_workflow_info` 
    - takes a dataframe containing the raw contents of a workflow export requested from the project builder
    - returns a list of tasks and details about each of them. Details in the initial comments of the script.

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
