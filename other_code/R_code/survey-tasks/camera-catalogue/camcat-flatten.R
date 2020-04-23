rm(list = ls())
library(tidyjson)
library(magrittr)
library(jsonlite)
library(dplyr)
library(stringr)
library(tidyr)
library(lubridate)


setwd(dir = "../survey-tasks/camera-catalogue/")
# CameraCatalogue is easy because you can only select ONE answer for any of the follow up questions. This script will not work if you can select >1 answer.

jdata_unfiltered <- read.csv("camcat_sa.csv", stringsAsFactors = F)

# So, need to limit to final workflow version and ideally split by task. 
jdata_unfiltered %>% group_by(., workflow_id, workflow_version) %>% summarise(., max(created_at), n()) %>% View

# Run things on filtered and unfilterd to compare
jdata <- jdata_unfiltered %>% filter(., workflow_version == 325.7)



############### SURVEY TASK
head(jdata)
for (i in 10:20) {
     jdata$annotations[i] %>% prettify %>% print
}

# preliminary flat

basic_flat_with_values <- jdata %>% 
     select(., subject_ids, classification_id, workflow_version, annotations) %>%
     as.tbl_json(json.column = "annotations") %>%
     gather_array(column.name = "task_index") %>% # really important for joining later
     spread_values(task = jstring("task"), task_label = jstring("task_label"), value = jstring("value")) 

# grab choices; append embedded array values just for tracking
# Note that this will break if any of the tasks are simple questions. You would need to split by task before here.
with_choices <- basic_flat_with_values %>%
     enter_object("value") %>% json_lengths(column.name = "total_species") %>% 
     gather_array(column.name = "species_index") %>% #each classification is an array. so you need to gather up multiple arrays.
     spread_values(choice = jstring("choice"), answers = jstring("answers")) #append the answers as characters just in case

# if there are multiple species ID'd, there will be multiple rows and array.index will be >1
with_choices %>% View
with_choices %>% summarise(., n_distinct(subject_ids), n_distinct(classification_id))
with_choices %>% group_by(., classification_id) %>% summarise(., count = n(), max(species_index)) %>% arrange(., -count)

# grab answers - for some reason, this keeps rows even if there are no answers! 
# Note that this last bit is the part that would need to be customized per team, I think
with_answers <- with_choices %>% 
     enter_object("answers") %>% 
     spread_values(how_many = jstring("HWMN"), which_side = jstring("WHCHSDFTHNMLSVSBL"))

with_answers %>% View
with_answers %>% summarise(., n_distinct(subject_ids), n_distinct(classification_id))
with_answers %>% group_by(classification_id) %>% summarise(., count = n()) %>% arrange(., -count)    

# You want to tie all of these back together just in case there are missing values
add_choices <- left_join(basic_flat_with_values, with_choices)
tot <- left_join(add_choices, with_answers)
flat_data <- tot %>% select(., -task_index, -task_label, -value, -answers)


basic_flat_with_values %>% summarise(., n_distinct(subject_ids), n_distinct(classification_id))
flat_data %>% summarise(., n_distinct(subject_ids), n_distinct(classification_id))


write.csv(flat_data, file = "flattened_camcat_sa.csv")

