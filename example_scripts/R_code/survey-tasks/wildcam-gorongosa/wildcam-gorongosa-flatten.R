rm(list = ls())
library(tidyjson)
library(magrittr)
library(jsonlite)
library(dplyr)
library(stringr)
library(tidyr)
library(lubridate)

#This project has subquestions that vary by species, including a howmany and select-all behaviors
jdata_unfiltered <- read.csv(file = "data/wildcam_gorongosa_test_raw.csv", stringsAsFactors = F)

# So, need to limit to final workflow version and ideally split by task. 
jdata_unfiltered %>% mutate(., created_at = ymd_hms(created_at)) %>% 
     group_by(., workflow_id, workflow_version) %>% summarise(., max(created_at), n()) %>% View

jdata <- jdata_unfiltered


head(jdata)
for (i in 15:20) {
     jdata$annotations[i] %>% prettify %>% print
}

# preliminary flat

basic_flat_with_values <- jdata %>% 
     select(., subject_ids, classification_id, workflow_version, annotations) %>%
     as.tbl_json(json.column = "annotations") %>%
     gather_array(column.name = "task_index") %>% # really important for joining later
     spread_values(task = jstring("task"), task_label = jstring("task_label"), value = jstring("value")) 


###----------------------------### SURVEY FLATTENING ###----------------------------### 

# grab choices; append embedded array values just for tracking
with_choices <- basic_flat_with_values %>%
     enter_object("value") %>% json_lengths(column.name = "total_species") %>% 
     gather_array(column.name = "species_index") %>% #each classification is an array. so you need to gather up multiple arrays.
     spread_values(choice = jstring("choice")) 

# if there are multiple species ID'd, there will be multiple rows and array.index will be >1
with_choices %>% View
with_choices %>% summarise(., n_distinct(subject_ids), n_distinct(classification_id))
with_choices %>% group_by(., classification_id) %>% summarise(., count = n(), max(species_index)) %>% arrange(., -count)


### FLATTEN WITH SUBQUESTIONS. NEED INPUT HERE.
#Single Choice Qs
count_string <- "HWMN" 
young <- "RTHRNNGPRSNT"
horns <- "DSNHRNS"

#Multi-Choice Qs
behavior_string <- "WHTBHVRSDS"



# grab answers - for some reason, this keeps rows even if there are no answers! 
# Note that this last bit is the part that would need to be customized per team, I think

with_answers_list <- with_choices %>%  #annoyingly, there's no easy way to unlist these. hence the hoop jumping in the next block.
     enter_object("answers") %>% 
     spread_values(how_many = jstring(count_string), 
                   young = jstring(young), 
                   horns = jstring(horns), 
                   behavior = jstring(behavior_string))


with_answers <- with_choices %>% 
     enter_object("answers") %>% 
     spread_values(how_many = jstring(count_string), # Grab all the single answer questions
                   young = jstring(young), 
                   horns = jstring(horns), 
                   behavior = jstring(behavior_string)) %>%
     enter_object(behavior_string) %>% #enter into the list of behaviors
     gather_array("behavior_index") %>% #gather into one behavior per row
     append_values_string("behavior") 

# spread answers (into separate columns): have to drop behavior index or else the rows won't combine!
with_answers_spread <- with_answers %>% data.frame %>% 
     select(., -behavior_index) %>%
     mutate(., behavior_present = 1) %>%
     spread(., key = behavior, value = behavior_present, fill = 0)

# spread answers (into a list)
test <- with_answers %>% data.frame %>% 
     select(., -behavior_index) %>% nest(behavior)


with_answers %>% View
with_answers_spread %>% View
with_answers_spread %>% summarise(., n_distinct(subject_ids), n_distinct(classification_id))

# the number of rows where count >1 should be the same as the difference between the row count for add_counces and basic_flat
with_answers %>% group_by(classification_id) %>% summarise(., count = n()) %>% arrange(., -count) %>% View   

# in theory, you want to tie all of these back together just in case there are missing values
add_choices <- left_join(basic_flat_with_values, with_choices)
tot <- left_join(add_choices, with_answers_spread)
flat_data <- tot %>% select(., -task_index, -task_label, -value)

#check that the number of distinct subject IDs and classification IDs is still the same
flat_data %>% summarise(., n_distinct(subject_ids), n_distinct(classification_id), n()) #flattened,
jdata %>% summarise(., n_distinct(subject_ids), n_distinct(classification_id), n()) #original

write.csv(flat_data, file = "sampledata/wildcam-flattened.csv")

