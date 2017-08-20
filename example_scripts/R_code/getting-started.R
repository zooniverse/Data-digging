library(tidyjson)
library(magrittr)
library(jsonlite)
library(dplyr)
library(stringr)
library(tidyr)

sas <- read.csv("data/questions-SAS.csv", stringsAsFactors = F) %>% head(., n = 1000)
kitteh <- read.csv("data/kitteh-zoo-classifications.csv", stringsAsFactors = F)
wilde <- read.csv("data/points-wildebeest.csv", stringsAsFactors = F)
chicago <- read.csv("data/chicago-wildlife-watch-classifications.csv", stringsAsFactors = F)


# so, annotations are arrays, whereas subject data and metadata are...json blobs?
sas$annotations[1] %>% prettify
kitteh$annotations[1] %>% prettify
wilde$annotations[1] %>% prettify
chicago$annotations[10] %>% prettify


for (i in 1:10) {
  chicago$annotations[i] %>% prettify %>% print
}
     


## Simple Markings

# revert to tidyjson for this...
wilde <- read.csv("data/points-wildebeest.csv", stringsAsFactors = F)
fun_check_workflow(wilde)

dat <- wilde %>% filter(., workflow_id == 78, workflow_version == 36.60) 
dat$annotations[1] %>% prettify

# basic jsonlite flattening function - doesn't really work. would need to get on with unlisting and so on.
test1 <- dat %>% basic_flattening() %>% mutate(., task_label = str_trunc(task_label,width = 30))
test1 %>% head


# Just get a look inside each marking
# note that document ID is the corresponding row number for the original data frame
# I have no idea why it's not letting me spread the values here, but that's easily done afterwards in tidy

# NOTE: if "value" is empty, then the row is just dropped. If you needed to, I suppose you could recombine with an extra layer of data manipulation: after flattening, then do a left join and force the columns to fill with NAs. This may explain why retirement rules and aggregation have discrepancies. 

# View the data
dat$annotations %>% as.tbl_json %>% 
     gather_array() %>%
     spread_values(task = jstring("task"), tasklabel = (jstring("task_label"))) %>%
     enter_object("value") %>%
     gather_array() %>%
     gather_keys() %>% 
     append_values_string() %>% View

## okay, so anything with a value length = 0 will get dropped as soon as you "enter the object." Let's grab those now.
wtest <- dat %>% head(., n = 100)

all_submissions <- dat %>% 
     select(., subject_ids, classification_id, user_name, workflow_id, workflow_version, created_at, annotations) %>%
     as.tbl_json(json.column = "annotations") %>%
     gather_array(column.name = "task_index") %>%
     spread_values(task = jstring("task"), task_label = (jstring("task_label"))) %>%
     gather_keys() %>%
     json_lengths(column.name = "total_marks") %>% 
     filter(., key == "value") 

empty_submissions <- all_submissions %>% filter(., total_marks == 0)

## To flatten inside of the dataframe, just specify the specific column. Note that the document.id is dropped, but the other reference information is kept.

#again, if you enter an object, then if that ebject is empty, the row will be dropped! Need to separately capture empty objects and recombine after the fact.

w_flat <- wtest %>% 
     select(., subject_ids, classification_id, user_name, workflow_id, workflow_version, created_at, annotations) %>%
     as.tbl_json(json.column = "annotations") %>%
     gather_array(column.name = "task_index") %>%
     spread_values(task = jstring("task"), task_label = (jstring("task_label"))) %>%
     enter_object("value") %>%
     gather_array(column.name = "mark_index") %>% #don't gather keys, whole point is that you are spreading out the damn keys.
     spread_values(tool_label = jstring("tool_label"), xcoord = jnumber("x"), ycoord = jnumber("y"), tool = jstring("tool"))



#check that this works. empty plus full should equal original total classifications.
unique(empty_submissions$classification_id) %>% length
unique(w_flat$classification_id) %>% length
unique(wtest$classification_id) %>% length


# recombine datasets: merge flat and empty (okay, do a full + meaty join)
# all_submissions - has one record per classification per subject
# w_flat has one record per mark per classification, but only if the counter >0

tot <- left_join(all_submissions, w_flat) # note that you have to drop array index because they reference two different things



############### SURVEY TASK
head(chicago)
for (i in 1:10) {
     chicago$annotations[i] %>% prettify %>% print
}


