## Working with B. Simmons’ aggregate-survey.py


This script is actually more versatile than the name suggests -  elements of it can be used to flatten the classification file for many task types, but the examples in the Zooniverse  Data digging repository have been slightly tailored to specific survey tasks – wildwatch_kenya and cleveland_wildlife.

To use this code one first has to prepare an environment for it.  The code was written in Python 2.7 which is an issue if (like me) you are running Python 3.  It uses a number of Python packages which you will need correctly installed, and calls two additional modules that are in the Zooniverse Data Digging example_scripts directory.

There are two options: prepare a virtual environment for Python 2.7 and the versions of the packages to match that, with no modification of the code needed, or prepare an environment for Python 3.x with current versions of the packages, and modify the code slightly to update it to Python 3.  For myself I had most of the packages needed already up and running with Python 3.62, and I did not want to “go backwards” so I took the second route.

The packages required beyond the “out of the box” Python 3.6 are pandas, numpy, ujson, and the two scripts get_workflow_info and aggregate_question_utils.

Details for Windows 7 installation for pandas and numpy are in “Working with Notes from Nature.md”   Unfortunately I migrated to Windows 10 prior to installing ujson.  Rather than reload all the python packages into the new set-up I simply copied the entire packages directory Python36-32\Lib\site-packages from my old Windows 7 set-up to the same location in the new installation of Python36-32 which resides in the x86 sandbox.  This works because Python 3.6 is still 32 bit and packages are nothing more than compiled python scripts – if Python can run in its new environment then any of the packages for that version of Python will run without modification – ie they can be copied across.

I suspect but have not tested pandas will install in Windows 10 without issues using 
pip install pandas

On the other hand numpy will likely be more difficult.  I would try what worked for Windows 7, or perhaps use the Pycharm package loader (under setup) but beyond those suggestions, I am sorry, you are on your own.  If you do not want to climb this particular hill you could look at using my own flatten_class_survey.py which is my usual building block approach to the same problem using only “out of the box” Python 3.6.

To get ujson to load in Windows 10 was a pain.  I had to first download and install Visual C++ Build Tools.  So 4 Gb and two hours later ujson installed from the Pycharm package loader in a few seconds.  Apparently ujson is not pure Python and needed two seconds of C++ building.  I suspect but have not tested that all the ujson calls could be converted to pure Python json.loads(). Ujson was used because it is faster but I will never recover two hours using it :)

Once the Python packages are installed, download a zipped copy of the Zooniverse Data digging repository if you have not already done so and extract the files to a known directory.  Create a new working directory for this project and copy the following files to it:

get_workflow_info.py 	(from example_scripts)

aggregate_question_utils.py 	(from example_scripts)

aggregate_survey.py 		(from wildwatch_kenya)


Download your_project-workflows.csv and your_project-workflow_contents.csv and copy these to the project directory.

Generate test data in your project and download your_project-classifications.csv. to the project directory.

To get things working I had to slice out one workflow and version from the classification download using flatten_class_frame.py. 


## Modifications to the scripts for Pyhton 3.x:

Using your editor load the scripts and modify them as noted below:

Line numbers are original line numbers (note aggregate-survey is the wildwatch_kenya version).

  aggregate-survey.py
	
lines 9, 10 ,11 ,13 ,14

switch data file and project workflow file names to match the file names from your project. Switch the workflow_id and version to match your data.

  get_workflow_info.py

line

    108  	tasknames = workflow_info.keys()

  	to:	tasknames = list(workflow_info.keys())

  aggregate_question_utils.py

line

    317	if not isinstance(a, basestring):

  	to:	if not isinstance(a, str):
      
  	340	if not isinstance(a, basestring):
      
  	to:	if not isinstance(a, str):

  	196	comment
      
  	to:	delete (optional)
      
  	197	for t, q in theqdict.iteritems():
      
  	to:	for t, q in theqdict.items():
	
Note that these are the only modifications I made to get this script to run on a standard survey project with one task and no vote fraction calculations.  Other branches I did not test may have more Python 2.7 to Python 3.x issues.
      

## Running aggregate-survey,py 

Despite modifying the classfile name in hardcoding, the script must be called with at least one argument – the classifications.csv file name which overrides the hardcoded filename: 

Python aggregate-survey.py your_project-classifications.csv

(From the Pycharm editor one can set the parameter script by right clicking on the green run arrow. Most other editors will have a similar function)

If you have not hardcoded the workflow_id and workflow_version info in lines 13, 14 you will have to add the appropriate parameters to the command line.  The command line will override whatever **is** hardcoded if you specify the parameters.

aggregate-survey.py yopur_project-classifications.csv   workflow_id=XXXX  workflow_version=XXX.XX

**Note Despite the fact this is suppopsed to allow this script to work on downloads with more than one workflow,  I was unable to run this script on a classification file with more than one workflow in it.  I did not attempt to debug this, I simply sliced out the one workflow and version using flatten_class_frame.py**

Attempt to run the script. If you get the instructions for usage and the parameter structures check you are supplying the correct files (and names), and the parameters are correct.

If you get a ‘dict-keys’ is not subscriptable error, verify you have correctly modified the scripts as noted above.  Debugg any other errors as best you can but at this point the scripts should be working as designed.

## The flattened survey output 

These scripts return three files. The first, with “_1lineeach” in the file name, is the flattened data. Note there is one line for each species identified in each subject.  There is the usual columns from the classification file:

classification_id	subject_ids	created_at	user_name	user_id	      user_ip
 
In addition there is a column for the choice made, plus one column for every sub-task question that was answered in any classification.  If the project had more than one survey task the columns for the next survey task follow.  If there are other types of tasks in the project there may be columns for those as well but not all tasks are completely broken out. Simple questions (single or multiple answer) should work, as should the “shortcut” questions used by some surveys  which as of this writing is experimental and not available through the standard project builder survey task.

The second file can be very confusing.  It has “_aggregated.csv” in the file name.  It has many columns sorted in alpha-numeric order.  This is only a subset though, of the columns in the larger file which has “_kitchensink” in the file name and like its name everything **and** the kitchen sink in it.

To understand these files consider an example project survey task with 25 animal choices and three questions, ("How many?" with 12 “bins”, "Behaviour?" with five options, and, "Are young present?" with yes or no options).  The kitchen sink version will have a column for the subject number, and a column for the total number of classifications done for that subject. Then for each animal choice there will be a column for the number of people that selected that animal in that subject, then a column for how many people answered the question “How many?” (not the answer to the question). Then comes a column for each of the twelve possible answers to that "How many?" question with the number of people that chose each answer. Then for each of the other questions there is a column for how many answered the question and a column for each possible answer choice. Just to make things difficult it is possible in the project definitions (in the questions csv file loaded into the project while building it) to pick and choose which questions are allowed for each species so **some** of the above columns can be missing.   If there were no “excluded” questions for say “Humans” or “Nothing here” the full kitchensink version for this survey would have 577 columns.

The “_aggregated.csv” file is simply only those columns, which for at least one subject, have a non-zero value.

From this file it is relatively easy to calculate vote fractions for any choice and answer option.  It would be up to a project team to pick out those that have significance for their project.


## Demo Files

The file   survey-classifications.csv   is a sample zooniverse classification file for a survey task built using the project builder and the template csv files provided there.

The file   survey-classifications_annotations_1lineeach.csv  is the flattened file output by aggregate-aurvey.py for the input file as noted above.

The file   survey-classifications_aggregated.csv is the “short” version of the aggregated file. For the above input.


