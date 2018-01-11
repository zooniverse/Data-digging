This is an attempt to open a repository of the scripts I have written for various zooniverse projects.
It is a work in progress.
 
I am not a professional coder - I deliberately use simple explicit code to make these scripts as easy to undersatnd and modify as possible - the goal is that they are useable by someone with minimal coding experience. To use most of them one needs to be able to follow some (hopefully) simple instructions.  These will include copying and pasting defined blocks of code, commenting out or "uncommenting" various lines of code, modifing some specified strings/and or variable names, and running the result in a python interpreter. Between the instructions, comments in the code, and the example demos someone with minimal coding experience (like me) should be able to extract their zooniverse data in a useable form from projects built with the standard project builder.

## Python environment and Editor

These scripts are written in Python 3.6.2.  They use as few additional packages as possible - the goal is to be able to run them with an out-of-the box Python set-up.  This is not always possible (eg plotting); in those cases I will provide a complete list of the required dependencies. 

Python is a relatively simple easy to learn programming language. It can be downloaded here: https://www.python.org/downloads/
You will also need a an editor. I recommend PyCharm Edu since it it intended to teach Python and provides tutorials but is also very easy to use as an editor and makes adding packages easy. It is free and available here: https://www.jetbrains.com/pycharm-edu/.   In addition I recommend an introductory text: A Byte of Python -  https://python.swaroopch.com/.   With these resources I was able to write useful scripts after reading the book and working through the PyCharm tutorial.

In general to use these scripts you will need to copy them to the editor and modify them following the instructions based on details you will know about your own project.  They are in a building block arrangement where you select the blocks you need and assemble a script to handle your project's data.

For some purposes (eg reconciling transcribed text) excellent solutions already exist and my purpose here is to prepare the output in a form that can directly use these solutions.  In most cases using these existing solutions requires additional packages specified by the third party, and getting those installed (particularly in Windows) is not trivial.  I have written readme's to assist with this were I can.

As with any programming language, Python needs exactly correct syntax to work.  As an object oriented language it is dependent on defined data structures and methods. Punctuation, spelling, and spacing are critical - most errors will result from small errors in these three things and the first step in any debugging should be a detailed check of the statements identified as in error at run time.  The second most common issue is index or key errors where we ask Python to work with a list or dictionary item that does not exist - usually due to a mismatch between the written script and the data we are feeding it - ie your data from your project is not matching the data structure the script expects - this usually requires a close review of the blocks chosen and the project workflow to ensure the correct blocks are being applied.

I hope to be able to provide help for the foreseeable future.  You can contact me through Zooniverse @Pmason.

## DBSCAN clustering script: Completed, with demo and readme

This DBSCAN clustering algorithm is intended for data sets which are limited to a few hundred points – it is not optimized for R-trees or large data sets, but works well for the data sets expected from drawing tool uses in zooniverse projects.
It is useful for aggregating the user data for various drawing tools (points circles etc). It is also useful for determining if a user placed more than one drawing tool within a close proximity to one already place within the same classifcation (ie testing for double clicks). It can also be used to test for drawing tools which were placed where no other user placed one - this can be used to test for the user's incidence of noise generation as a measure of their competance or as a test for bots.

## Flatten classification file building blocks

This group of scripts is my approach to the problem of flattening (ie simplifying and breaking apart) the JSON formatted strings in the Zooniverse classification download.  This is directed at project owners with little IT support using the project builder to create their project. Like the project builder the effort is made up of a basic framework on which blocks are added - basically the correct blocks are added to handle the output from each particular task in the project. Each block of code must be slightly modified in a easy to understand way to match the project's task labels so the output data is labeled in a way the project owner expects.
The following modules or blocks are availabe or planned:
#### 1) The basic framework with ability to Slice the Classification file in various ways to select the pertinent records. Completed, with slicing demo and readme.
This will provide the framework the other blocks will be added onto. By itself it can be used to slice (ie to select specific records) the Classification file based on various conditional clauses using specificed fields in the classification records.

#### 2) General utility blocks to provide some simple functions that make the output file more useful: Completed, with two demos and readme. 
  -	user_name This block replaces not-logged-in user_name based on an external picklist prepared elsewhere and keyed off user_ip.  The scripts to generate a picklist can use ip or browser data to group the not-logged-in users.
  -	image_number These blocks attempt to get subject image metadata from the subject_data field and generate a image identifier that may be more significant to the project owner or alternately, merge a cross-reference csv file into the flattened output file. The cross reference file is generated elsewhere and could have additional fields such as geo-references. The image_number (and possibly other info) will be (a) field(s) in the output file to aid analysis.  The external cross reference file is read in its entirety into memory.  If it is a very large file this may strain computing resources.  In that case one could use the slice function of the Frame to break the task into blocks by subject number.  Alternately a script could be written to handle a customized file merge later – the effort to set one up is likely more than the effort to break the task into chunks and run the job piecemeal :)
  -	elapsed_time This block pulls the started and finished times from the metadata field and calculates the elapsed time the user spent on the classification.
  -	image_size This block attempts to pull the natural height and width for the subject image from the metadata file. This can be used for various scaling operations for plotting, clustering or for testing out-of-bounds drawing tools.

#### 3) Task specific blocks that handle the various task types allowed by the project builder.  The following blocks are planned. Those with an asterix are written and working in some form:
- Question with single answer (Complete)
- Question with Multiple answers (Complete)
- Drawing tool - Single tool type, no sub-tasks (Complete)
- Drawing tool - Sub-tasks (Complete)
- Drawing tool - Multiple tool types in one task (Complete)
- Transcription - Single field (Complete)
- Transcription - Mark and transcribe or comment (Complete)
- Survey - Using B. Simmons' aggregate-survey.py (Complete)
- Survey - Building block approach including flattening aggregation and filter/reconcile results (Complete)

## Basic Aggregation

Normally several volunteers classify each subject.  There are clear benefits with the “wisdom of the crowd” both to reduce the possibility of “fat finger” accidental inputs or careless or even malicious inputs, but also to take advantage of the diversity of education, life experience, and many other factors that in a net total have been shown to often exceed the ability of a single individual to cut through uncertainty, preconceptions and biases.

What this means for a project owner is of course, that a set of inputs for a specific subject need to be compared and the consensus or crowd wisdom determined for that set of data.

The first step of this process, once the data has been flattened and simplified, is to collect it together subject by subject.  This process is known as aggregating the data.

### Two Approaches:

There are two main approaches.  One is to use advanced database techniques such as offered by pandas – a Python package which is commonly used for working with large data sets.  The other approach is more of an old fashioned do it yourself aggregation routine.  The pandas route needs the package added to your Python environment and is less intuitive.  It is also a bit of using a sledge hammer to place tacks.

The approach I will advocate will use Python out of the box with no add-ons needed.   It may be a little more code intensive, but in the end I believe just as fast and efficient, not that we need to do this so frequently that speed and computer resources are a concern.

To aggregate the data we need to determine by which field we want to group the flattened classification records.  This is normally the field subject_ids, but it may be in some cases such as a survey task a combination of fields such as subject-choice.  To describe the process we will call whatever field we want to group by the “selector” and assume we have flattened the classification file so the selector is in a field (column) by itself, and all records have a value there of a consistent sortable data type – usually a string. 

### Sort the flattened classification records: 

The first order of business is to sort the flattened classification file using the selector as the sort key.  All the heavy lifting is actually done in this stage – once the file is sorted we will only need to work with one record at a time.  If the file is huge (ie several gigabytes) resources to sort it in one go may be a problem.  But we can slice the raw classification download by the selector field in to chunks of whatever size we want when we flatten the data – and since we are slicing by the selector, each section will have no cross contamination with any other section and they can be sorted and aggregated independently.  

So the first script in this section is a basic sort routine written as a function.  This is a very general routine with many potential uses beyond the use in question.  As written it cleans up and deletes the unsorted file but this can be optional – just drop out the last few lines where the existence of the old file is tested and if it exists deleted.  The function accepts an input file, sorts on any field specified by a integer (first field is ‘0’), and writes the sorted data to a specified output file.  The actual sort order is not critical – What we need is all the classifications with the same selector grouped together in a block in the data file – we start accumulating at the first record of the block and continue to the last record with that selector.

### The aggregation routine: aggregate_frame.py

Once the file is sorted by the aggregator, the aggregation routine itself is fairly simple:
1)	initialize empty bins for each field where we want to aggregate the data.
2)	initialize the first value of the aggregator to a empty value.
3)	Set up to loop over the records of the sorted field in order and read a record.
4)	Test if the record just read matches the current value of the selector:
If it does NOT we know we have come to a section of the file with a new selector.  In this case, if this is not just the first record we will output the aggregated and accumulated data for the fields we have collected.
In any case we will reset the selector to the new value, and reset the bins so they only contain this record’s values of their respective fields.

Otherwise if the record’s value of the selector’s field matches the current selector then we want to add the data from each field into its respective bin and move on to the next record. (Actually do the aggregation)

5)	Once all records are read we need to catch the last set of accumulated data which was being collected when we ran out of records.

### Further processing within the aggregation loop:

Note once we get to the step where the selector has changed and our bins are full we can do much more than just output them.  We can process, filter, resolve, cluster or otherwise work with the aggregated data in any way we want before we move on to the next group.  We just need to remember to do the last set of bins as well.

There are various ways to aggregate and process the fields

–	Strings that represent numbers can be converted to numbers and added.  Standard stats can be applied to numbers – Average, median etc.

–	Strings can be gathered as elements in a list which is appended for each record.  These can then be passed to other routines for reconciliation.

–	More complex fields need to be read with a json.loads() and may themselves be lists or lists of lists. These can be aggregated into larger Python objects.

–	Drawing objects in general are aggregated by collecting together the points that define each of the drawings being aggregated.  A set of circles for example gives a set of points for the various locations of the centres.  The centre points can be clustered – which automatically groups circles placed nearly in the same position by various volunteers.  Clustering sorts all the circles placed on the image into different target areas. (At least it does if they are separated by more than the discrepancies between volunteers marking the same centre point)  Once clustered, the radii of each group of circles could be averaged or we could use the median value. Points can be accumulated then clustered in the same manner.  The more complex drawing figures are still defined by points so similar things can be done to resolve the consensus figure.

–	Transcriptions and survey tasks have their own unique issues – full aggregation techniques for these are available and discussed elsewhere.

–	Sometimes we may only want to count things – eg if the field holds “yes” or “no”, we may simply want to count instances of “yes” so that the aggregated bin is the count of positive responses to a question.

–	We may then want to calculate vote fractions by dividing such counts by the number of records that matched the selector.

–	If we were clever when we flattened the data file we may have created objects that are easy to aggregate – such as answer-vectors with 1’s and 0’s for each possible response indicating that response selected or not.  Adding the corresponding elements of these together and dividing by the total number of records that matched the selector results in an aggregated answer vector which give each response option directly as a vote fraction.

–	We may be able to process the aggregated data for a subject using Bayesian probability theory – In this case each value in some group of aggregated field values represents a yes or no “opinion” concerning the likelihood of some event. (example the existence of an object in the image by the placement of a point)  Beginning with some estimate of the probability of the event, each opinion can be applied in turn to modify this estimate if we know something about the probability that opinion is correct, specifically the probability the observer is correct when they predict such events to occur (ie accurately mark real objects) and the probability they are correct when they predict the event will not occur (accurately do not mark non-existent objects).  The sequential application of these opinions to improve the current estimate probability of the event, each corrected for their skill or reliability, is referred to as a Bayesian pipeline.  


Just about any manipulation of the data that is dependent only on the aggregated results for that selector can be done at the stage the accumulated bins are ready to output. 

It is practical to expect the output of the aggregation stage is a simplified set of data by subject with most or all the minor discrepancies in the individual classifications reconciled or resolved to reveal the consensus result.   The consensus result is often expressed as a plurality vote fractions for each question response, clustered drawing objects, or “best fit” transcriptions.

Further analysis beyond this point will depend more on the science in the data than its form.


## Plot overlays

A useful way of displaying aggregated drawing data is to show the drawings and/or the consensus drawing as a overlay on the original subject image as in example 4982655.jpg in the repository.  This shows the original subject image with the centre points for all the circles that the volunteers drew on it during classification.  These points were then clustered using aggregate_drawing_demo.py, and the circles in the figure show the clusters that were made, along with a summary of the number of points in each cluster.

This figure has been produced using Python and Matplotlib, a Python package for plotting.   Unfortunately to use this, one must successfully load a number of Python packages – this will not work with out-of–the-box Python.

### Python Environment and Matplotlib Installation.

It can be a pain, particularly for Windows users, to get the necessary packages installed.
Matplotlib requires a number of packages; for the full list refer to the Installation instructions at:  https://matplotlib.org/users/installing.html

I was on Windows 7 professional the first time I installed Matplotlib and I used the wheels from http://www.lfd.uci.edu/~gohlke/pythonlibs after many hours trying unsuccessfully to get a third party package loaders like Anaconda and Canopy and WinPython to work.

Once Matplotlib and the dependencies were loaded and working I worked through a few of the example plots at https://matplotlib.org/gallery/index.html#pyplot-examples to make sure everything was working.   

### Files in the repository:

•	aggregate_drawing_demo.csv  - the aggregated, clustered data sample - See the Basic_aggregation repository for how this file is created.

•	lookup_url.py - pulls subject and url from the subject download by subject set and workflow_id – Can easily be modified for other uses where specific fields need to be set up in a table.

•	lookup_list_subject_url.csv – the lookup list data for subject set 7369 and workflow 3130.

•	plot_data_interactive_aerobotany.py – the plot routine customized for Aerobotany.

•	plot_data_interactive.py – the basic generic plot routine  - a starting point for other projects

•	4982655.jpg – a sample jpeg format saved plot

•	4982655.fig.pickle – a sample pickle file for the above plot.

•	pickpickles.py – a script to find and select pickled files to display using matplotlib. This file could be used to find and load any pickle file with every few modifications to how the pickle file is activated in the last few lines.


Note that lookup_url.py and pickpickles.py are actually quite general and with little modification could be used for many purposes beyond their specific use here.




## Panoptes Client

The Python Panoptes Client allows one to write scripts that can do all what can be done via the project builder and much more. Below are listed a number of scripts written to address speific requirements. I will add more as the need for them arises.

### Subject_uploader

A simple UI allows one to upload image files from a local directory with a minimum of hassle – Uplike the project builder subject uploader, it can be interrupted while processing and be resumed without duplicating or missing files in the directory, and it produces a report of exactly what files were uploaded so you are sure everything is correct.

There are two versions of this script.  subject_uploader.py is written in Python 3.6, while subject_uploader_2,py is written in Python 2.7  Both have been tested with small subject sets only, but with a stable internet connection should work fine for larger sets.  In any case error handling should carry the process through any errors and the final part of the script produces a file with the filenames of the subjects that were successfully uploaded for verification.

Both scripts work the same way.  
First the script connects with the Panoptes Client using your zooiniverse User_name and Password. These have to be set as environmental variables for your computer using your OS.  Alternately these can be hardcoded in the script if you keep it private enough.  The project slug "pmason/fossiltrainer" must be replaced to match that for your project, and you must have collaborator or owner status on the project.

Second, a minimal UI asks for the path to the image files to be uploaded.  The script will find all image files in that directory and attempt to upload them. It is important that the directory only contain image files you want uploaded.  Non-image files are ignored so it is quite practical to place a copy of the script in the directory and run everything from that directory as the current working directory.

Next the UI asks for the display_name for the subject set you want to create or use.  The script will search for the subject set and prepare to add to it if it exists or create it if new.

There is then a confirmation step where the number of files to upload and where they are to be added can be verified before proceeding.

Once that is done the script proceeds to determine what files if any are in the subject set already.  It then attempts to upload any files that are naot already uploaded to the subject set.  This can take some time.  The file names are displayed as each file upload is completed and the subject has been linked to the subject set.

The final step queries the subject set directly and produces a file containing the filenames of all the subjects in the subject set at the end of the uploading process.  This can be used, along with the subject set counts, to verify all the subjects were uploaded correctly.

### Generate Classification and Subject exports

The script generate_export.py logs into the Panoptes client using User_name and Password previously set up as Environmental Variables in your Operating system.  Alternately these can be hardcoded if the code is kept secure to protect your password. It is also necessary to hardcode the desired project slug in line 7 to use the script as a stand-alone rather than a module.

The script first tests to see if 24 hours have elapsed since the last classification export was requested, and warns and terminates if not. If the last export request is more than 24 hours previous it attempts to generate a new one.  The script then waits 30 seconds for Panoptes to begin to create the export and then tests to see if that has happened. If not it warns the export request is not being produced.

These same steps are then repeated for the Subject export.

### Download exports and slice

The script download_export_and_slice.py logs into the Panoptes client using User_name and Password previously set up as Environmental Variables in your Operating system.  Alternately these can be hardcoded if the code is kept secure to protect your password. It is also necessary to hardcode the desired project slug in line 7 to use the script as a stand-alone rather than a module.
The destination path and filenames for both the classification file and the subject export need to be hardcoded, as well as the locations for the sliced output to use the script as a stand_alone, or explicitly passed to the functions if called as modules. 


Unlike the code suggested in the Panoptes Client documentation, this script can handle large export files (easily > 1Gb) since it does not read the file into memory all in one go but streams the data to a file in chunks. All subsequent operations from the file after they are opened for slicing are handled by Python to avoid overloading the memory available.

The download and slicing can take several minutes for larger files (about 3 minutes per Gb for my hardware, internet connection and when zooniverse is not too busy - all three things will affect the time.)

The script determines the age of the classification export file based on the current time and the last update to the export.  This age is calculated for EST - other time zones will need to change the hardcoded offset to zulu time.  If the export file has not completed generating, the download will fail with the message 'Classifications download did not complete' and the function returns False.

If the generated export file exists it is then downloaded to the file specified as the destination.  This operation is handled by the Python package requests using request.iter_content and has been quite robust. You may be able to optimize it slightly for your situation by changing the chunk size though 4096 works well for me.  Once the file is complete a message to that effect is printed, and the function returns True. If the download fails for any reason the error is handled, a warning message is printed and the function returns False

The script then does the same for the subject export.  If other exports are required, minor modifications of this function can handle the other exports as well.

The next function slice_exports uses an only slightly modified flatten_class_frame.py to set up logical tests for records to be included in the slice. See the documentation for that script for details.  The specific limits and conditions need to be hardcoded based on your project workflows, subject sets and subject id ranges.  (Note classification export files have a field subject_ids with an s while the subject export has subject_id with no s)

Using the appropriate conditions and limits any part of either of the exports can be extracted into much smaller files for further processing.  Since it is likely that the reduced classification file will be processed multiple times for various purposes it makes sense to do the slice once per download rather than leave it to the flattening step, though further slicing can be done there as well.

The script supplies a short report of records read and processed (sliced) into the shortened files.  If the functions complete with no errors they return True.

###  Copy Subject Set

This script is written in Python3.62 and requires the panoptes_client to be installed.

To use the script your zooniverse user-name and password must be set in your Operating System as Environment Variables for the keys User_name and Password. Alternately you can hardcode your username and password in the code as shown below but then you must secure the code to protect your password..

````Panoptes.connect(username='user_name', password='password')````

If you attempt to connect to a project for which you are not authorized as a owner or collaborator the script will respond 

````subject set not found or not accessible````

Unfortunately the error handling is very crude and does not tell you exactly what went wrong.

The script first asks you for the source project id and the subject_set name, and attempts to access this subject set.  If the set is not found or is not accessible to you have the option to try again or exit. It is best to copy and paste the subject set name directly from the project builder since it is both case sensitive and spaces and punctuation count.

The script then queries the subject set and creates a list of subjects in it that need to be copied to the destination.  This can take some time - many minutes for large sets.

The script then asks for the project id and subject set name for the destination subject set.  Again an attempt to access a project you do not have access to will produce the output

````Project not found or accessible````

with the opportunity to try again or exit.

The script then locates the destination subject set or proceeds to create it and link it to the specified project.  The script then proceeds to link the subjects in the list from above one at a time verifying they linked to the new subject set for each subject. Subjects in the destination subject set previously linked or those that did not link due to communication errors or other causes will report 

````previously linked or did not link correctly````

The total number of subjects linked is reported.  If some subjects were already linked to the destination subject set this number will not be the same as the length of the list of source subjects.

The script then queries the new subject set directly and produces a list of the subjects linked to it.  That list should be the same length as the source subject set. The list is saved to a file  'copied_subjects.csv'.  Again this takes a few minutes.  





