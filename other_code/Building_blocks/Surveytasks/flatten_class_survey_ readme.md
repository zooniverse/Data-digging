# Survey tasks:

In the Classification download, the user's responses to each task are recorded in a field called 'annotations' (including those of experts and those tagged "TRUE" for being gold standard responses. The field is a JSON string. When loaded into Python using the json.loads() function from import json it becomes a dictionary of dictionaries of form {{....}, {.....}, {....}} with a dictionary for each task the user is required to complete, in the order completed.

The form of the individual dictionaries for the tasks depends very much on what type of task it is - a question, drawing tool, transcription or survey task.

This set of scripts is for a survey task.

## Flattening the survey data:

To start, a copy of flatten_class_frame.py is modified with a block added to deal with the survey task.  As usual with this building block approach, the file locations, any tests for which classificiation records to include (usually a specific workflow_id and workflow_version), and the fieldnames for the output file need to be hardcoded.

For survey tasks though, the specific task number (eg T0 in this case) is used to recognize the survey task and initiate the block's action so that needs to be determined from the data and modified in the survey block.  As well, to interpret the questions and structure the output files, we need to know all about the project details - fortunately most of what we need to know is conveniently summarized in the questions.csv file used to build the project. With a copy of that file included in the file locations list, most of the heavy lifting for the details is done - though we still need to chose field names for the output columns we want and link those with the appropriate answer variables in the writer statements. For later ease of aggregation one field called "all_choices" should be provided for a flag indicating multiple choices in a classification and the answer-vector for all possible questions and responses for that classification. There must also be a field for 'subject_choice' which is a simple concatenation of the subject and choice.

One other major change from the usual flatten_class_frame.py setup is we want to write an output line for each subject-species combination recorded in each classification.  This requires moving the write action **inside** the block analysing the survey task - so any other task blocks to analyse any other tasks in the project, or provide any other general utilities must be inserted ahead of the survey task block.

The output from this basic survey task block has three sections - One section is the normal columns identifying classification, user and subject data, and the analysis of any other tasks we added in for this project. The second section is the flattened survey data in the columns as chosen above. This section can look (by choosing the order and text for the fieldnames) exactly like the output for B Simmons' aggregate_survey.py which is in survey-classifications_annotations_1lineeach.csv.  The third section is the essentially the same information in a form easy to aggregate. It has all the survey questions and their possible responses in a answer-vector format.  This section also must have a field for 'subject_choice' for the following aggregation to work. 

## Aggregating the survey data:

### Sorting by subject_choice

One of the downsides for **not** using something like pandas is that we need to write our own aggregation routines to select out records by a specific field and accumulate over those fields we want to aggregate.

The first step is we need to sort the entire flattened file on the fields we are going to select on - in this case 'subject-choice' The next section is a general sort routine which is quite useful in itself.  We simply run it on the output file of the first section.  The routine automatically deletes the unsorted file but this can be easily modified if their is a reason to keep the unsorted file.

### Build a record of total classifications

To calculate vote fractions for a choice or response, we will need the total number of classifications made and if any of those classifications identified more than one choice within the classification.  The next section simply aggregates the classifications done and a counter that will alert us to multiple choice classifications went we attempt to interpret and filter the results.

### Aggregate over subject-choice

We build an old fashioned aggregation routine which calculates the total number of classifications where each choice or response was made.  That number divided by the classifications made and converted to percent becomes a vote-fraction for that choice or response for that subject-choice.  These are output as an aggregated answer-vector which reports the percent vote fraction for every possible question/response for each subject-choice.

This format is very compact compared to the "kitchensink" format of B Simmons' survey-classifications_aggregated_kitchensink.csv but surprisingly still has **all** the information that file has.

This summary of the data shows us some obvious cases were there is incomplete agreement between volunteer's classifications, and also where there is good or perfect consensus.  The next step is to define some rules to resolve or reconcile those situations where there was less than perfect agreement.  

## Filtering the aggregated data

The following filter was written based on my own thoughts but hopefully in a way that the limits can be adjusted to align the results with a project team's requirements.  Up to this point the scripts will work with any survey task and any questions set, but at this point the first question is assumed to be a how_many question with the possible answers as an array of ordered "bins" corresponding to increasing counts of the choice(species) reported. 

This filtered file has no counterpart in B. Simmons' repository but obviously the projects using aggregate_survey.py must have done something similar starting from the format returned by those scripts.

The output after the filter has been applied could be returned in a vector format but the script I have supplied here outputs the data in a columnar format.  To this end the fieldnames for the columns containing the answers to the second and subsequent questions/responses must be chosen and hardcoded.  It is assumed there will be as a minimum, a column for subject, choice, choice vote-fraction, the how_many consensus and a vote_fraction for that consensus, plus one column for each question/response aggregate vote_fraction for the rest of the questions. Any other columns defined in the aggregate file can be brought forward as well.  
If you need help to modify the filter for your needs, contact me at @Pmason at zooniverse.


````'''
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
            
6)  No other filters are applied to the other questions with a simple v_f recorded.````

 


