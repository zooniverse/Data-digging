rm(list = ls())
library(tidyjson)
library(magrittr)
library(jsonlite)
library(dplyr)
library(stringr)
library(tidyr)

source(file = "../generalized/flattening_script.R") 
chicago <- read.csv("chicago_sample_version397.csv", stringsAsFactors = F)


# So, need to limit to final workflow version and ideally split by task. 
# T0 is clearly the only task we really care about in this dataset (though note the changed format of current site). 
# This script deals with the version that has "wow" as a subquestion instead of a follow up task.

check_workflow(chicago)
chicago %<>% filter(., workflow_version == 397.41)

for (i in 10:20) {
     chicago$annotations[i] %>% prettify %>% print
}

# quick summary of the data
chicago %>% summarise(n(), n_distinct(classification_id), n_distinct(subject_ids))

# preliminary flattening
basic_flat_with_values <- chicago %>% 
     select(., subject_ids, classification_id, workflow_version, annotations) %>%
     as.tbl_json(json.column = "annotations") %>%
     gather_array(column.name = "task_index") %>% # really important for joining later
     spread_values(task = jstring("task"), task_label = jstring("task_label"), value = jstring("value")) 

View(basic_flat_with_values)

# quick check the filtered original data
chicago %>% summarise(., n_distinct(subject_ids), n_distinct(classification_id), n_distinct(workflow_version))
basic_flat_with_values %>% summarise(., n_distinct(subject_ids), n_distinct(classification_id), n_distinct(workflow_version))

# grab choices; append embedded array values just for tracking
# Note that this will break if any of the tasks are simple questions. You would need to split by task before here.
chicago_choices <- basic_flat_with_values %>%
     enter_object("value") %>% json_lengths(column.name = "total_species") %>% 
     gather_array(column.name = "species_index") %>% #each classification is an array. so you need to gather up multiple arrays.
     spread_values(choice = jstring("choice"), answers = jstring("answers")) #append the answers as characters just in case

# if there are multiple species ID'd, there will be multiple rows and array.index will be >1
chicago_choices %>% View
chicago_choices %>% group_by(., classification_id) %>% summarise(., count = n(), max(species_index)) %>% arrange(., -count)

# grab answers - for some reason, this keeps rows even if there are no answers! 
# Note that this last bit is the part that would need to be customized per team, I think
chicago_answers <- chicago_choices %>% 
     enter_object("answers") %>% 
     spread_values(how_many = jstring("HWMN"), wow = jstring("CLCKWWFTHSSNWSMPHT"), off_leash = jstring("CLCKSFDGSFFLSH"))

chicago_answers %>% View     
chicago_answers %>% group_by(classification_id) %>% summarise(., n())     

# in theory, you want to tie all of these back together just in case there are missing values
add_choices <- left_join(basic_flat_with_values, chicago_choices)
tot <- left_join(add_choices, chicago_answers)
flat_data <- tot %>% select(., -task_index, -task_label, -value, -answers)

View(flat_data)
write.csv(flat_data, file = "projects/sample_data/flattened-chicago-397.csv")

