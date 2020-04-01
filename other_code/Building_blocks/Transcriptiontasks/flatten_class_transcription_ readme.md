In the Classification download, the user's responses to each task are recorded in a field called 'annotations' (including those of experts and those tagged "TRUE" for being gold standard responses. The field is a JSON string. When loaded into Python using the json.loads() function from import json it becomes a dictionary of dictionaries of form {{....}, {.....}, {....}} with a dictionary for each task the user is required to complete, in the order completed.

The form of the individual dictionaries for the tasks depends very much on what type of task it is - a question, drawing tool, transcription or survey task.

This set of scripts is for transcription tasks.

## Types of transcription tasks:

A simple transcription task has the form {"task":"TX", "task_label":"instructions the users saw", "value":"text entered"}.

This is pretty simple, especially if one knows which of the blocks in annotations we are dealing with. Even without that we can find the correct task because we know the **wording** of the instruction text.  (Due to the way the project builder can be assembled, it is unlikely tasks are numbered in the order completed, and with the conditional branching allowed, tasks are not even in the same order in every response.)

Drawing tasks which use a drawing tool such as the rectangle can be used to mark or highlight text in a document which is then transcribed in a sub-task of each drawing/mark. We have seen in flatten_class_drawing.py how to split out drawings and sub-tasks.  Here we need go one step further and separate the use of each drawing tool into the drawing/location part, and the transcription itself with each part in its own field/column in a csv file. Block 2 is used when only **one** usage of each tool colour is allowed.

However, if multiple uses for each drawing tool are allowed, the analysis becomes much more difficult. As we see below, we will want each transcription to be in a column by itself. Unless the maximum number of drawings is specified in the drawing task we do not know how many field names and columns to set up to handle all the possible locations and transcriptions. Further we would not know what order the drawings were made, and which to reconcile without analysing their locations in the text.  Block 3 below handles the special case where a fixed maximum number of uses of one tool (eg one colour of rectangle for instance) are allowed but locations can be simply sorted and **ordered** from top to bottom of the image. To match locations which are not simple to group or order by vertical position only, we would need to aggregate over the various user classifications for a subject, find common locations marked by the volunteer’s and group the transcriptions from those common locations to reconcile.  My intention is to explore this in future Aggregation techniques but it is beyond simply flattening the classification file.

Note:  these blocks assume the rectangle is used as the marker but any of the tool types could be used eg points, circles, ellipses - in that case modify parameters (x, y, etc) in the drawing and the output list (see the function definitions in Block 3 of flatten_class_drawing.py. for the required lists.)

## Reconciliation of the transcriptions between users:

Transcriptions are difficult to aggregate. Unless multiple volunteers input the exact same thing, down to capitalization, spacing and punctuation, simple conditional matching is inadequate and some sort of reconciliation between the multiple answers must be done.  However this problem has been solved rather well by the Notes From Nature team, and we can use their expertise. We need to get the data from your specific project into a format that can use their code to reconcile the responses. 

See https://github.com/juliema/label_reconciliations

It is not a trivial task to get set up to use their code - it requires a number of additional python packages be installed and familiarity with passing arguments to the main module at execution. See the readme in this repository on this topic.

While it was written specifically for their somewhat customized Zooniverse interface, their code has the ability to reconcile any appropriately prepared csv file. The scripts in flatten_class_transcription.py break out the classification record so each text which is to be reconciled with other volunteer's entries is in a field by itself with a unique field name in a csv file suitable to input directly into nfn's reconcile.py.


## The blocks available in flatten_class_transcription.py:

Block 1 Simple transcription tasks - one instruction results in one text block 

Block 2   ONE use only of multiple instances (colours) a drawing tool type to mark different things which are transcribed in a sub-tasks for each tool usage.

Block 3 One tool (type and colour) used a known maximum number of times on one subject.  Each use must be separately placed from top to bottom so that a simple sort by vertical location places each drawing and its sub-task transcription in the appropriate output column. (example - sequential entries 
such as logs or diaries)

## The Demo:

The demo flatten_class_transcription_demo.py takes a classification where up to five dates have been marked using one tool and transcribed two ways in a two step sub-task - first a verbatim transcription, then as a specific date format. Each tool usage is sorted by its location from the top of the page down and each location and the two dates are given their columns in the output.  Then a simple transcription of one specific line is pulled out and given its own column as well. This results in a csv file where each transcription is in a designated column.  The output file is in a format that can be directly reconciled with Notes from Natures reconcile.py appropriately set up with the csv file parameter and the column names we want to reconcile. See the command line below.

To build the demo we start with flatten_class_frame.py, drop unneeded sections, and add in the necessary blocks from flatten_class_transcription.py with slight modifications specific to the project task labels.  As well there is a modification to split out the dual sub-task into transcription_0 and transcription_1 (see the demo code).  At this time an odd wrinkle in reconcile.py requires the normal column subject_ids (with an ‘s’) to be called subject_id (with no ‘s’)

Included in the repository is the raw classification file: example_classifications.csv,  the flattened output file: flatten_class_transcription_demo.csv, and nfn’s reconciled output file: reconciled_trans_demo.csv as well as the reconciliation summary: summary_trans_demo.html

The actual command line for nfn’s reconcile.py for this demo is:
reconcile.py -f csv -c "transcribed_1:text,formatted_1:text,transcribed_2:text,formatted_2:text,transcribed_3:text,formatted_3:text,transcribed_4:text,formatted_4:text,transcribed_5:text,formatted_5:text,first line:text"
-r data\reconciled_trans_demo.csv
-s data\summary_trans_demo.html
--user-column user_name 
data\flatten_class_transcription_demo.csv

