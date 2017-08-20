This directory contains R code for handling Zooniverse data, especially flattening and aggregating classification data.

For more, less well-developed, R code, including the R notebooks at www.rpubs.com/aliburchard, please see www.github.com/aliburchard/dataprocessing

**getting-started:** This script just introduces you to working with JSON if you want to explore how Hadley Wickham's tidyjson works a bit. There's more like this at www.rpubs.com/aliburchard.

## Point Marking
**wildebeest-flatten:** Flattening code for the Serengeti Wildebeest Count (https://www.zooniverse.org/projects/dl-j/serengeti-wildebeest-count)
Note that in this flattened file, every mark gets its own row. There are existing clustering algorithms in R that should work fairly well on this data.

## Survey-tasks

### Generalized 
This folder contains code that should work on *most* PFE survey tasks.

**flattening-wrapper:** This provides a wrapper around the flattening-script.R, in which you specify your project, identify and subset your dataset to the relevant workflows, and identify your various question types (e.g. your "how many", "yes/no", or "select-all-that-apply" question fields.) This calls the flattening-script.R code and produces a flat file for you to save. Note that if you have shortcut questions, you will need to flatten those separately and integrate into your dataset. See the example script for Kenya Wildlife Watch for examples.

**flattening-wrapper-noninteractive:** If you already know your project specifications (e.g. workflow ID and version, question fields, etc), you can store them in a separate file and call them here. This is possibly useful once you've tested your initial flattening interactively, and now flatten your complete dataset.

**flattening-script:** This includes all of the functions for actually running the flattening, and indeed, a function that actually *runs* the flattening code.

**aggregate-survey:** Aggregation is in less generalizable shape than the flattening code. This script works for Michigan Wildlife Watch, Wildcam Gorongongosa, and basically any project that has any of the standard survey task question types: "how many", "yes/no", "select all that apply." *Note* how many is a special type of a "single choice" question, in that the answers are treated as an ordinal factor and the min/median/max values are reported. This code does not yet handle more standard "single choice" questions, that, say ask the user to select one answer from a variety of answers. 

**aggregate-functions:** This contains all of the functions called in aggregate-survey.R. This could really use a function that takes the median value of an ordinal factor (that would be called in the "how many" extraction.

### Michigan
Code to flatten *and* aggregate a pretty standard survey project. This includes the generalized flattening code as well as an older script that walks you through the JSOn exploration step by step. Note that this code calls the **flattening-script** and **aggregate-functions**.


### Kenya
This flattens Kenya Wildlife Watch, which is a mostly standard survey task except that it uses a shortcut button for nothing here. The annotations from the shortcut button are flattened separately and then recombined. This code currently just adds "nothing here" as a new column to the annotation, but you would actually want to fill in the "Choice" field with that as your species choice, so that you can aggregate that normally. Note that this code calls the **flattening-script**.

### Chicago
This has scripts that flatten a couple of different versions of the Chicago project. Note that in cases like this, the research team may need to combine data from multiple different workflows - if species names or data formats have changed, then this will require some manual effort to recombine multiple flattened files prior to aggregation.

### Camera Catalogue
This provides a flattening script for Camera Catalogue data, which is a pretty simple survey task. This code walks you through the JSON parsing step by step.

### Wildcam Gorongosa
This walks you through flattening and aggregating Wildcam Gorongosa step by step.

