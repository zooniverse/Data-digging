rm(list = ls())
library(tidyjson)
library(magrittr)
library(jsonlite)
library(dplyr)
library(stringr)
library(tidyr)

source("functions/quick_functions.R")
# This projects has both FOLLOW UP QUESTIONS as well as a "check all that apply" formatted subquestion, meaning that the classification data are a bit different 
# THIS IS BASICALLY THE MOST COMPLEX PROJECT FORMAT.

# jdata_unfiltered <- read.csv(file = "data/michigan-zoomin-classifications.csv", stringsAsFactors = F)
# check_workflow(jdata_unfiltered) %>% View
# set_workflow_version <- 463.55
# jdata <- jdata_unfiltered %>% filter(., workflow_version == set_workflow_version) %>% head(., n = 5000)
# write.csv(jdata, "projects/sample_data/michigan-sample.csv", row.names = F)

jdata <- read.csv("projects/sample_data/michigan-sample.csv", stringsAsFactors = F)


############### SURVEY TASK
head(jdata)
for (i in 15:20) {
     jdata$annotations[i] %>% prettify %>% print
}

# preliminary flat - split out question from survey tasks

basic_flat_with_values <- jdata %>% 
     select(., subject_ids, user_name, classification_id, workflow_version, annotations) %>%
     as.tbl_json(json.column = "annotations") %>%
     gather_array(column.name = "task_index") %>% # really important for joining later
     spread_values(task = jstring("task"), task_label = jstring("task_label"), value = jstring("value")) 

View(basic_flat_with_values)

#just have a quick look at the different components
basic_flat_with_values %>% 
     gather_keys %>%
     append_values_string() %>% 
     group_by(., workflow_version, key, task) %>% 
     summarise(., n())

#--------------------------------------------------------------------------------#
# split into survey vs. non-survey data frames. Question is flattened and can be exported as a separate file now.
survey <- basic_flat_with_values %>% filter(., task == "T3")
question <- basic_flat_with_values %>% filter(., task == "T2") 

###----------------------------### SURVEY FLATTENING ###----------------------------### 

# grab choices; append embedded array values just for tracking
with_choices <- survey %>%
     enter_object("value") %>% json_lengths(column.name = "total_species") %>% 
     gather_array(column.name = "species_index") %>% #each classification is an array. so you need to gather up multiple arrays.
     spread_values(choice = jstring("choice")) 

# if there are multiple species ID'd, there will be multiple rows and array.index will be >1
with_choices %>% View
with_choices %>% summarise(., n_distinct(subject_ids), n_distinct(classification_id))
with_choices %>% group_by(., classification_id) %>% summarise(., count = n(), max(species_index)) %>% arrange(., -count)

# grab answers - for some reason, this keeps rows even if there are no answers! 
# Note that this last bit is the part that would need to be customized per team, I think

with_answers <- with_choices %>% 
     enter_object("answers") %>% 
     spread_values(how_many = jstring("HOWMANYANIMALSDOYOUSEE")) %>%
     enter_object("WHATISTHEANIMALSDOING") %>% #enter into the list of behaviors
     gather_array("behavior_index") %>% #gather into one behavior per row
     append_values_string("behavior") 

# spread answers (into separate columns): have to drop behavior index or else the rows won't combine!
with_answers_spread <- with_answers %>% data.frame %>% 
     select(., -behavior_index) %>%
     mutate(., behavior_present = 1) %>%
     spread(., key = behavior, value = behavior_present, fill = 0)

with_answers %>% View
with_answers_spread %>% View
with_answers_spread %>% summarise(., n_distinct(subject_ids), n_distinct(classification_id))

# the number of rows where count >1 should be the same as the difference between the row count for add_counces and basic_flat
with_answers %>% group_by(classification_id) %>% summarise(., count = n()) %>% arrange(., -count) %>% View   

# in theory, you want to tie all of these back together just in case there are missing values
add_choices <- left_join(survey, with_choices)
tot <- left_join(add_choices, with_answers_spread)
flat_data <- tot %>% select(., -task_index, -task_label, -value)

#check that the number of distinct subject IDs and classification IDs is still the same
flat_data %>% summarise(., n_distinct(subject_ids), n_distinct(classification_id), n()) #flattened,
jdata %>% summarise(., n_distinct(subject_ids), n_distinct(classification_id), n()) #original

write.csv(flat_data, file = "projects/sample_data/michigan-flattened.csv", row.names = F)

