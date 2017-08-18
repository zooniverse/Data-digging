rm(list = ls())

library(tidyjson)
library(magrittr)
library(jsonlite)
library(dplyr)
library(stringr)
library(tidyr)
library(lubridate)

source(file = "projects/survey-tasks/generalized/flattening_script.R") 

############## INTERACTIVE - CLEANING OF CLASSIFICATION DATA AND SPECIFYING FIELDS ###################

# You will need to define variables that will be used in the run_json_parsing function. They need the names as below.

# REQUIRED VARIABLES: You NEED TO DEFINE THESE or the script could break.
# jdata <- "character"
# survey_id <- "character"
# workflow_id_num <- numeric
# workflow_version_num <- numeric (e.g. 45.01). you need to include the entire version (even if it's 45.00)

# OPTIONAL VARIABLES
# single_choice_Qs <- "character" or c("character", "character")
# single_choice_colnames  <- "character" or c("character", "character")
# multi_choice_Qs  <- "character" or c("character", "character")
# multi_choice_colnames <- "character" or c("character", "character")


# Specify Project
project_name <- "michigan"
classifications_file <- "data/michigan-zoomin-classifications.csv"


# Examine data
jdata <- read.csv(classifications_file, stringsAsFactors = F)

# Set project-specific details
check_workflow(jdata) %>% View
workflow_id_num <- 2276
workflow_version_num <- 463.55

# limit to relevant workflow id and version
jdata <- jdata %>% filter(., workflow_id == workflow_id_num, workflow_version == workflow_version_num)

# Identify task-specific details. These variable names are important, because I haven't figured out how to define them in the function call 
# (there's some weird referencing. I don't know. The function definitions and scripts could be improved, but things seem to generally work.)
View_json(jdata)
survey_id <- c("T3")
single_choice_Qs <-  c("HOWMANYANIMALSDOYOUSEE")
single_choice_colnames  <-  c("how_many")
multi_choice_Qs <- c("WHATISTHEANIMALSDOING")
multi_choice_colnames <- c("behavior")


# Flatten by calling the code from the flattening_functions file. This isn't the cleanest approach, but it'll have to do.
# If you want to combine multiple workflows or multiple tasks before aggregating, this is the time to do it.
final_data <- run_json_parsing(data = jdata)

View(final_data)
write.csv(final_data, file = paste0(classifications_file, "-flattened.csv"), row.names = F)


### The Data out will be in the following format: 
# Metadata
# Species (Choice)
# single choice questions
# multiple choice questions, with the colnames prepended to the values

# For example:
# subject_ids: unique Zooniverse subject identifier. you will need to link this back to your primary key via subject metadata.
# user_name: registered user name or "not-logged-in-hash" where hash is the user's hashed IP address
# classification_id: a unique key representing that classification. This will be unique to the user and subject, but can encompass multiple tasks
# workflow_version: the major and minor version of the workflow
# task_index: an index of tasks. Usually will be 1 if this is your only task.
# task: the task identifier, e.g. "T0"
# task_label: <NA> for survey tasks, but for follow-up questions, this would be the text of the question itself
# value: the annotation data in an embedded list (that is saved as a character). This is really just for double checking against.
# total_submissions: The total number of submissions a user made for a give species/choice. So, if they said lion, 1, standing and leopard, 1, standing, this = 2.
# submission_index: Reflects the index of the particular choice. Not really important.
# choice: Your species choice. NOTE that if you have multiple workflow versions and change species names, you'll need to reconcile these.
# how_many: note that this is not actually a NUMBER, and be careful that you don't treat it as one, especially if you have ranges like 3-5 that get saved as 35.
# behavior_EATING: Every possible answer for a "select all that apply" question gets it's own column, so that you can calculate the proportion of users who marked them present.
# behavior_INTERACTING
# behavior_MOVING
# behavior_RESTING
# behavior_STANDING