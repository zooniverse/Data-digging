## Basic Aggregation readme

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

### Aggregate_drawing_demo

This demo takes the basic aggregation routine set out above and applies it to the circles used to mark the three types of tree canopy in the original Amazon Aerobotany project.
It uses the flattened classification file produced in flatten_class_drawing_demo.py.
The centre points for each type of canopy are collected into a list of points.  When all the classifications for a subject are collected together, each lists of points is clustered using a density based clustering routine (see elsewhere in this repository for more information on DBSCAN). (Note the version used here is a very minor modification of that routine – it keeps track of the eps used since it is not constant here – it is scaled from the image size for each subject.  The eps is returned as part of the cluster tag which lists the number of points in, and the location for each cluster.

Each cluster of circle centres represents where at least min_points = 5 people placed circles close enough together that they formed a cluster within the scaled eps).   Since they were asked to circle particular types of tree canopy, these clusters represent the consensus locations of those canopies which we can count or map in a further analysis.  (Here they are counted, though later we will use this file output to plot them on the original images as an overlay).

The volunteer is attempting to enclose what can be odd shaped and diffuse objects with a circle - the precision of the circle placement is not perfect.  It becomes a trade off for the clustering routine for how diffuse the cluster can be ( ie how big eps is).  Too large and two nearby canopies can fuse together and only count as one, too small and canopies where the points were more widely spaced do not cluster.  In the actual Aerobotany analysis we used different ranges of eps for the different types of canopies and utilized the circle radii to scale eps dynamically based on the size of the canopy in question.  With those sorts of refinements we were able to get the artefacts introduced by the clustering process itself to be small compared the ability of the consensus to correctly identify the canopy types in question.  

For another example of the aggregation routine in use look at flatten_class_survey_demo.py in the Surveytasks directory of this repository.  In that script the basic choice question is aggregated with a vote_fraction calculated for each subject-choice combination.  The balance of the questions are aggregated as an answer-vectors using the summation over the selected/not selected 0 and 1’s to derive a vote fraction for each possible response option.   In that example the aggregated data is then passed to a further optional filter to determine the consensus and resolve discrepancies if possible or flag them if there is no strong consensus.. 
