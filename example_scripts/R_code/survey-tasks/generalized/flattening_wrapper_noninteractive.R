# Alternative to the flattening_wrapper, you can define the project specs in a different file and just call them here

rm(list = ls())

library(tidyjson)
library(magrittr)
library(jsonlite)
library(dplyr)
library(stringr)
library(tidyr)
library(lubridate)

source(file = "projects/survey-tasks/generalized/flattening_script.R") 
source(file = "projects/in-development/project-specs.R")

jdata <- read.csv(classifications_file, stringsAsFactors = F)
jdata <- jdata %>% filter(., workflow_id == workflow_id_num, workflow_version == workflow_version_num) 
final_data <- run_json_parsing(data = jdata)
write.csv(final_data, file = paste0(project_name, "-flattened.csv"))
