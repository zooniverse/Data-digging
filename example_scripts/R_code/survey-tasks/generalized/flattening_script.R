
library(tidyjson)
library(magrittr)
library(jsonlite)
library(dplyr)
library(stringr)
library(tidyr)
library(lubridate)


###################### EXPLORE DATA #######################
# Need to evaluate and limit to proper subsets

# check workflow
check_workflow <- function(data){
     data %>% group_by(workflow_id, workflow_version) %>%
          summarise(date = max(created_at), count = n()) %>%
          print
}


# View classifications and dates of workflows to limit data out to proper workflow version and number

View_json <- function(jdata) {
     for (i in 1:50) {
          jdata$annotations[i] %>% prettify %>% print
     }
}

####################### FLATTEN ####################### 
# Data formats:
# choice is standard and always one item.
# answers is standard and contains a list of multiple values, some of which can be arrays. Empty arrays are handled differently than empty lists.
# how interpretable the text is, and whether you need to link to workflow content to get vowels, depends on when the project was uploaded.

# This code is meant to be run on a single workflow version. 


# FLATTEN TO TASK
# Highest order flattening to extract relevant tasks *within* a classification. 

flatten_to_task <- function(json_data) {
     flat_to_task <- json_data %>% 
          select(., subject_ids, user_name, classification_id, workflow_version, annotations) %>%
          as.tbl_json(json.column = "annotations") %>%
          gather_array(column.name = "task_index") %>% # really important for joining later
          spread_values(task = jstring("task"), task_label = jstring("task_label"), value = jstring("value"))
     return(flat_to_task)
}  

# Sometimes projects have multiple tasks - either shortcut questions or follow-up questions (or even marking!). 
# These all need to be flattened separately. This function filters to the relevant task you need.
filter_to_task <- function(flat_to_task, task_id = NA) {
     if (!is.na(task_id)) {
          # For some unknown reason, updating dplyr breaks how filter handles json objects. Hence the super base R filtering.
          out <- flat_to_task[flat_to_task$task == task_id, ]     
     } else {
          out <- flat_to_task
     }
     return(out)
}


# Flatten shortcut questions
# Whereas normal questions are already flattened, shortcut questions are contained inside of an array. 
flatten_shortcut <- function(shortcut_data) {
     shortcut_data %>% 
          enter_object("value") %>% # all of the annotation information is contained within this value column, which is named by the call in the previous code chunk.
          gather_array(column.name = "shortcut_index") %>% # each classification is an array. so you need to gather up multiple arrays.
          append_values_string() 
}


# GRAB CHOICES
# species_key is defined at entry or else defaults to choice
# produces one row per species/submission per classification. If a user selects "lion" twice, this counts as two submissions.
get_choices <- function(survey_data) { 
     with_choices <- survey_data %>%
          enter_object("value") %>% # all of the annotation information is contained within this value column, which is named by the call in the previous code chunk.
          json_lengths(column.name = "total_submissions") %>% # Note that if users submit multiple classifications for a single species, this will be off.
          gather_array(column.name = "submission_index") %>% # each classification is an array. so you need to gather up multiple arrays.
          spread_values(choice = jstring("choice")) # "choice" is hardcoded as a key name in the zooniverse data. if this changes, this script will need updating.
     return(with_choices)
}     

# GRAB SINGLE ANSWER QUESTIONS
# Single Choice Questions (e.g. how many, are there young, horns, etc.) 
# These can be Yes/No *or* have >2 choices. I guess that can be dealt with in aggregation.

#Single Choice Qs

# This function is a helper function in the get_single_choice_Qs part of the script. It basically allows you to spread apart multiple single choice columns.
spread_single_choice_values <- function(x, names, values) {
     stopifnot(length(names)==length(values))
     do.call("spread_values", c(list(x), setNames(as.list(values), names)))
}

# This dives into the answers field (the json data) and into the fields that have single choice answers
get_single_choice_Qs <- function(with_choices_data, cols_in, cols_out) {
     if (!exists("single_choice_Qs")) {
          print("You have not entered any Single Choice subquestions, such as 'how many?', 'are there any young?', or 'do you see anything really cool?'")
          single_choices <- NULL
     } else {
          if(missing(cols_out)) cols_out <- cols_in
          print("Getting single-choice questions.")
          print(paste("The subquestion", cols_in, "will be returned as", cols_out)) # paste returns a 1:1 (so three returns for three columns); cat returns all at once
          
          single_choices <- with_choices_data %>% 
               enter_object("answers") %>% 
               spread_single_choice_values(cols_out, 
                                           lapply(cols_in, jstring)
               ) #lapply(strings, jstring) just makes everything a jstring.
     }
     return(single_choices) 
}



# GRAB MULTI ANSWER QUESTIONS
# Multi Choice Questions (eg. behaviors, which sides are visible)
# Annoyingly, you need to separately do this for every multiple choice question and then recombine into a single multi-choice dataset. 
# The list trick that works for single choices doesn't work here.
get_multi_choice_Qs <- function(with_choices_data, cols_in, cols_out) {
     
     if (!exists("multi_choice_Qs")) {
          print("You have not entered any Multiple Choice subquestions, such as 'what behaviors do you see?', 'what sides of the animal are visible?'")
          combined <- NULL
     } else {
          if(missing(cols_out)) cols_out <- cols_in
          print("Getting multi-choice questions.")
          print(paste("The subquestion", cols_in, "will be returned as", cols_out)) # paste returns a 1:1 (so three returns for three columns); cat returns all at once
          
          stopifnot(length(cols_in) == length(cols_out))
          combined <- with_choices_data
          
          for (m in 1:length(cols_in)) {
               #col_in    <- multi_choice_Qs[m]
               #col_out   <- multi_choice_colnames[m]
               
               col_in    <- cols_in[m]
               col_out   <- cols_out[m]
               array_ind <- paste(col_out, "ind", m, sep=".")
               prepend   <- as.character(col_out)
               
               multi_choice_m <- with_choices_data %>% 
                    enter_object("answers") %>%
                    enter_object(col_in) %>%
                    gather_array(column.name = array_ind) %>%
                    append_values_string(col_out) 
               
               # Spread columns
               midway <- multi_choice_m %>% data.frame %>%
                    select_(., paste0("-", array_ind)) %>% #have to paste these for standard evaluation
                    mutate(., value_present = 1, pre_col = prepend) %>%
                    unite_(., "out", c("pre_col", col_out)) 
               
               #holler if any weirdness with duplicate entries in the answers
               check_duplicate_answers <- midway %>% 
                    group_by(subject_ids, user_name, classification_id, submission_index, choice, out) %>% 
                    mutate(dups = n()) %>% 
                    filter(dups > 1) 
               check <- check_duplicate_answers %>%
                    nrow() %>% 
                    as.numeric()
               
               if(check > 0) {
                    print("These classifications have duplicate answers for given questions; these answers are being removed.")
                    print(check_duplicate_answers)
               }
               
               multi_choice_m_flat <- midway %>%
                    distinct(subject_ids, user_name, classification_id, task, total_submissions, submission_index, choice, out, value_present) %>%
                    spread_(., key = "out", value = "value_present", fill = 0)
               
               # Need to left_join after creation of each new columns because there might be multiple rows per classification, and this could vary.
               combined <- left_join(combined, multi_choice_m_flat)
          }
     
     return(combined)     
     }
}


## RUN THE FUNCTIONS AND COMBINE EVERYTHING
# This doesn't actually take any function arguments besides the dataset. 
# Should probably rewrite so that this runs the checks for column names in this function and does whatever assigning is necessary.
# Really,none of these functions *actually* use functions in the right way, but oh well.

run_json_parsing <- function(data) {
     # Run checks on data input (assigns columns out so that you don't need to tweak it in the next section)
     # Note that all of these variables are defined by the wrapper
     
     if(!exists("survey_id")) print("You need to specify the task ID for the survey task.")
     
     if(!exists("single_choice_Qs")) print("You have not specified any single choice questions")
     if(!exists("single_choice_colnames")) {
          if(exists("single_choice_Qs")) 
               single_choice_colnames <- single_choice_Qs
     } 
     
     if(!exists("multi_choice_Qs")) print("You have not specified any multi choice questions")
     
     if(exists("multi_choice_Qs")) {
          if(!exists("multi_choice_colnames")) 
               multi_choice_colnames <- multi_choice_Qs
          if(exists("multi_choice_colnames")) {
               if(length(multi_choice_colnames) != length(multi_choice_Qs)) {
                    stop("Your multi-choice columns out do not equal the columns in")
                    geterrmessage()
               }
          }
     }
     
     
     
     
     # Now run through all of functions to flatten everything
     flattened <- flatten_to_task(json_data = data) %>% filter_to_task(task_id = survey_id) #Produces one row per classification. Useful when wanting to recombine other, potentially breaking, task types.
     choices_only <- get_choices(flattened) # grabs all of the choices. Can produce >1 row per classification.
     single_choice_answers <- get_single_choice_Qs(choices_only, cols_in = single_choice_Qs, cols_out = single_choice_colnames) #cols_out is optional
     multi_choice_answers <- get_multi_choice_Qs(choices_only, cols_in = multi_choice_Qs, cols_out = multi_choice_colnames) #cols_out is optional
     
     # now combine everything
     full_data <- flattened
     if(!is.null(choices_only)) full_data <- left_join(flattened, choices_only)
     if(!is.null(single_choice_answers)) full_data <- left_join(full_data, single_choice_answers)
     if(!is.null(multi_choice_answers))  full_data <- left_join(full_data, multi_choice_answers)
     return(full_data)
     
     
}

