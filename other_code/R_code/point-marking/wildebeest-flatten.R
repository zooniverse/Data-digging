library(tidyjson)
library(magrittr)
library(jsonlite)
library(dplyr)
library(stringr)
library(tidyr)

source("quick_functions.R") #adds a check workflow and view json function

# Note you'll want to set working directory as appropriate.
wilde <- read.csv("wildebeest_2016_sample.csv", stringsAsFactors = F)

check_workflow(wilde)

# Filter to the relevant workflow version. You might want to combine multiple versions; it depends on the changes that have been made to the project.
dat <- wilde %>% filter(., workflow_id == 78, workflow_version == 36.60) # note this is an older version of the workflow given the sample data.

View_json(dat)
dat$annotations[1] %>% prettify


# View the data structure, note that anything with zero length "value" field is dropped
dat$annotations %>% as.tbl_json %>% 
     gather_array() %>%
     spread_values(task = jstring("task"), tasklabel = (jstring("task_label"))) %>%
     enter_object("value") %>%
     gather_array() %>%
     gather_keys() %>% 
     json_lengths() %>%
     append_values_string() %>% head %>% View

# Grab the top-level info for ALL classifications
# produces one row per classification per subject; final column indicates how many x-y coordinates were made in that classification.
all_submissions <- dat %>% 
     select(., subject_ids, classification_id, user_name, workflow_id, workflow_version, created_at, annotations) %>%
     as.tbl_json(json.column = "annotations") %>%
     gather_array(column.name = "task_index") %>%
     spread_values(task = jstring("task"), task_label = jstring("task_label")) %>%
     gather_keys() %>%
     json_lengths(column.name = "total_marks") %>% 
     filter(., key == "value") 

# produces one row per mark per classification per subject, but only keeps classifications with >0 marks
flattened <- dat %>% 
     select(., subject_ids, classification_id, user_name, workflow_id, workflow_version, created_at, annotations) %>%
     as.tbl_json(json.column = "annotations") %>%
     gather_array(column.name = "task_index") %>%
     spread_values(task = jstring("task"), task_label = (jstring("task_label"))) %>%
     enter_object("value") %>%
     gather_array(column.name = "mark_index") %>% #don't gather keys, whole point is that you are spreading out the damn keys.
     spread_values(tool_label = jstring("tool_label"), xcoord = jnumber("x"), ycoord = jnumber("y"), tool = jstring("tool"))



#check that captures all the data. should equal original total classifications.
# dat %>% summarise(., n(), n_distinct(classification_id), n_distinct(subject_ids)) #original data
# all_submissions %>%  summarise(., n(), n_distinct(classification_id), n_distinct(subject_ids)) # this maintains one row per classification.
# all_submissions %>% filter(., total_marks == 0) %>% summarise(., n(), n_distinct(classification_id), n_distinct(subject_ids)) # number of "empty" classifications
# flattened %>% summarise(., n(), n_distinct(classification_id), n_distinct(subject_ids)) # number of non-empty classifications

original_class <- n_distinct(dat$classification_id)
empty_class <- n_distinct(filter(all_submissions, total_marks == 0)$classification_id)
nonempty_class <- n_distinct(flattened$classification_id)

ifelse(empty_class + nonempty_class == original_class, "yay", "boo")

# recombine datasets: merge flat and empty (okay, do a full + meaty join)
# all_submissions - has one record per classification per subject
# flattened has one record per mark per classification, but only if the counter >0

tot <- left_join(all_submissions, flattened) 

data_out <- tot %>% 
     mutate(., task_label = str_trunc(task_label, width = 25)) %>%
     select(., -task_index, -key)

write.csv(x = data_out, file = "flattened-wildebeest_2016_sample.csv")
