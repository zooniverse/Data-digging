#Pulsar Hunters Analysis

Was originally at @vrooje's [pulsar-hunters-analysis](https://github.com/vrooje/pulsar-hunters-analysis) repo.

This project was launched during the BBC's Stargazing Live programme, which means that we started receiving classifications on a Monday evening and needed to have the first set of pulsar candidates (ranked by probability, cleaned of known pulsars and artifacts) by Tuesday midday, and a final list incorporating all further classifications by Wednesday evening. So there are some things that could be improved about these scripts with a bit of tweaking, which there was not time for during the actual analysis stage.

There are 2 Python scripts, both of which use the classifications csv file that's in this directory.

 - `aggregate_pulsarclass.py` - Does a full aggregation of the classifications, including user weighting based on gold standard information, incorporation of Talk tags, and different treatment of Talk comments and classifications by science team members. In order to do this, it reads from the classifications export and breaks out the task from the annotations json, so there are examples of dealing with annotations here as well as dealing with gold-standard data.

 - `make_count_file_for_treemap.py` - counts classifications by user and assigns each user a color code, outputting them to a file that is readable by `treemap.R`.

 The other script here is `treemap.R`, an R program to create a visualization of classifications provided by user. There are examples of these online, if you'd like to see some before trying out this code, which I'd recommend given that this program can take a *very* long time to run for a large project. If you can't find a good example online, consider running it on a subsample of users, say, 1000 of them. (For the full project user list it took the code something like 24 hours to run. And its output is a single raster image.)
