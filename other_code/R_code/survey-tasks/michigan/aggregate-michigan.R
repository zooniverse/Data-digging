rm(list = ls())
library(dplyr)
library(magrittr)
library(stringr)
library(tidyr)

setwd("../michigan/")
source("../generalized/aggregate_functions.R")

raw_data <- read.csv("michigan-flattened.csv")
# note that the total_species count reported here isn't accurate when users report the same species multiple times. 
head(raw_data)

raw_data %>% summarise(n_distinct(subject_ids), n_distinct(classification_id)) 

raw_data %<>% 
     group_by(subject_ids) %>% # count up the number of distinct classification IDs
     mutate(., num_class = n_distinct(classification_id)) %>% #because there will be >1 row per classification_id if >1 spp
     arrange(., subject_ids, classification_id) 
raw_data %>% View

#Need to Identify behavior columns, how many columns, etc. Let's get data input out of the way now.
howmany_column <- "how_many" # this is a special kind of single-answer column. 
single_answer_cols <- NULL # no single-answer columns here, other than how many, which gets special treatment.
multi_answer_cols <- names(select(ungroup(raw_data), starts_with("behavior"))) #the flattening script handily appends this to the front of behavior columns.


# NOTE THAT YOU NEED TO PROVIDE THE MAPPING LATER ON IF YOU USE A HOW MANY COLUMN. I CAN'T SEEM TO GET THE FUNCTION TO ACCEPT VARIABLES. 
# So, ignore these for now. Ideally we'd just have a function that can take the median of a factor.
# howmany_map_from <- c("1", "2", "35", "610", "MANY")
# howmany_map_to <- c("1", "2", "4", "8", "20") # need to provide a numeric map (at least until I can write a function to get medians for ordered factors)
# lookup_list <- as.character("'1' = '1', '2' = '2', '35' = '4', '610' = '8', 'MANY' = '20'")



########### CLEAN UP MULTIPLE VOTES PER USER ###############
# number of different species should match the number of submissions per user.
# research team needs to decide how to combine duplicate entries per user. 
# Easiest thing is to just take the first submission, though most robust thing is probably to combine the answers.
# Note: this will be difficult without knowing what is a count, etc. Research teams can create their own, or, hoping it's relatively rare, just drop the extras.

check_spp_counts <- raw_data %>% 
     group_by(subject_ids, classification_id) %>% 
     mutate(., num_species = n_distinct(choice), check_num_spp = n()) 

#check for duplicates
bad_counts <- check_dups(raw_data)

# can just run this - sets cleaned_classifications to the correct dataset, dropping duplicates where necessary
if(is.null(dim(bad_counts))) {
     print("No duplicates to drop")
     cleaned_classifications <- check_spp_counts
} else {
     # NOTE that I don't know how you combine different answers for a single choice questions, thus, this just takes the FIRST anser
     print(paste("Dropping", dim(check_dups(raw_data))[1], "duplicate classifications"))
     
     cleaned_classifications <- raw_data %>% group_by(subject_ids, classification_id) %>% 
          mutate(., num_species = n_distinct(choice)) %>%
          group_by(., subject_ids, classification_id, num_class, num_species, choice) %>% 
          #summarise_all(., sum) # adds up counts for duplicates of spp, only works if everything is numeric
          summarise_all(., first) # takes the first record per user per species classification
}



check_dups(cleaned_classifications)


####################### AGGREGATE! #######################

 
##### SUBJECT-LEVEL METRICS

subject_metrics <- cleaned_classifications %>% ungroup %>%
     group_by(., subject_ids) %>%
     mutate(., num_votes = n(), # if a  user ids >1 spp, there will be more votes than classifications
            diff_species = n_distinct(choice)) # count the total number of different species reported by different users, for pielous score

glimpse(subject_metrics)

# Calculate aggregate number of species per subject by taking the median number of species reported across all volunteers, and tie back to subject metrics.
species_counts <- cleaned_classifications %>% ungroup %>%
     group_by(subject_ids, classification_id) %>%
     summarise(total_spp_by_user = mean(num_species)) %>% #Need to select only one row per classification_id, then summarise across those. 
     summarise(., agg_num_species = round(median(total_spp_by_user), 0))#aggregate species count, which is median rounded up
     
glimpse(species_counts)

cleaned_classifications <- left_join(subject_metrics, species_counts) %>% ungroup
glimpse(cleaned_classifications)


####### SPECIES-LEVEL METRICS

### For each species, aggregate counts and behavior votes. ###
# okay, so there's a difference between the proportion of VOTES and the proportion of classifications. 
# If some users ID >1 species in a single species image, there will be more votes than classifications. 
# The opposite is true for when some users only ID 1 species in a multi-species image.


#this provides one row per species ID per classification. We actually don't really need all the grouping variables... could just pull them apart and save for later.
grouped_classifications <- cleaned_classifications %>% 
     select(., -num_species) %>% # these aren't relevant
     group_by(., subject_ids, num_class, num_votes, agg_num_species, diff_species, choice) # fields at subject level or higher

#Tally the votes for each species ID'd within a subject
species_votes <- grouped_classifications %>% 
     # for every species within a subject, aggregate votes.
     summarise(., votes = n_distinct(classification_id)) %>% #count up the number of votes per species choice
     mutate(propvote = votes/sum(votes), #calculate proportion of votes for this species
            propclass = votes/num_class) #calculate proportion of classifications for this species
     
# Tally votes for the different behaviors (or other multi-choice feature) for each species. 
multi_answer_votes <- grouped_classifications %>% 
     summarise_at(., .cols = multi_answer_cols, funs(calc_prop))

# 
# # Tally votes for factor questions with single answers
# yes_no_votes <- grouped_classifications %>% 
#      summarise_at(., .cols = yesno_columns, funs(calc_yes))
# 


howmany_votes <- grouped_classifications %>%
     mutate(how_many = dplyr::recode(as.character(how_many), '1' = '1', '2' = '2', '35' = '4', '610' = '8', 'MANY' = '20')) %>%
     mutate(how_many = as.numeric(how_many)) %>%
     summarise_at(., .cols = howmany_column, funs(med_count = median, min_count = min, max_count = max))

# Okay, so the full dataset has all of the aggregate votes per species. The only thing left is to select the top n species for each subject.
all_data <- full_join(species_votes, howmany_votes) %>% full_join(., multi_answer_votes)

write.csv(final_dat, file = "data/michigan_aggregation.csv")
