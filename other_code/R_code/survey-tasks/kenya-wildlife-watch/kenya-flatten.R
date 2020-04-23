rm(list = ls())

library(tidyjson)
library(magrittr)
library(jsonlite)
library(dplyr)
library(stringr)
library(tidyr)
library(lubridate)

setwd("../kenya-wildlife-watch/")
source(file = "../generalized/flattening_script.R") 

############## INTERACTIVE - CLEANING OF CLASSIFICATION DATA AND SPECIFYING FIELDS ###################

# You will need to define variables that will be used in the run_json_parsing function. They need the following names:

# REQUIRED VARIABLES
# jdata
# survey_id
# workflow_id_num 
# workflow_version_num 

# OPTIONAL VARIABLES
# single_choice_Qs 
# single_choice_colnames 
# multi_choice_Qs 
# multi_choice_colnames


# Specify Project
project_name <- "kenya"
classifications_file <- "kenya-sample.csv"

# Examine data
jdata <- read.csv(classifications_file, stringsAsFactors = F)

# Set project-specific details
check_workflow(jdata) %>% View
workflow_id_num <- 2030
workflow_version_num <- 307.77

# limit to relevant workflow id and version
jdata <- jdata %>% filter(., workflow_id == workflow_id_num, workflow_version == workflow_version_num) 

# Identify task-specific details. These variable names are important, because I haven't figured out how to define them in the function call 
# (there's some weird referencing. I don't know. The function definitions and scripts could be improved, but things seem to generally work.)

View_json(jdata)
survey_id <- "T3"
single_choice_Qs <-  c("HOWMANY", "ARETHEREANYYOUNGPRESENT") # if the length of the columname vectors don't match, you'll get an error 
single_choice_colnames  <-  c("how_many", "young")
multi_choice_Qs <- c("WHATBEHAVIORSDOYOUSEE")
multi_choice_colnames <- c("behavior")

shortcut_id <- "T5"

# Flatten by calling the code from the flattening_functions file. This isn't the cleanest approach, but it'll have to do.
# If you want to combine multiple workflows or multiple tasks before aggregating, this is the time to do it.
survey_data <- run_json_parsing(data = jdata)



# ADD the nothing here questions back in. 
# Eventually would be good to add this bit back into the flattening script itself, though it could get complicated if multiple answers for a shortcut question, like in Serengeti.
final_data <- flatten_to_task(json_data = jdata) %>% 
     filter_to_task(task_id = shortcut_id) %>%
     flatten_shortcut(.) %>% select(classification_id, string) %>% 
     left_join(survey_data, .) %>%
     rename(empty = string)



View(final_data)
write.csv(final_data, file = paste0(project_name, "-flattened.csv"))
