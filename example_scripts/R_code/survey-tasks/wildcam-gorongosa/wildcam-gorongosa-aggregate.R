library(dplyr)
library(magrittr)

data <- read.csv("data/wildcam-flattened.csv")

data %>% summarise(n_distinct(subject_ids), n_distinct(classification_id)) 

data %<>% select(., -X, -workflow_version, -task, -total_species, -species_index) %>% #these get in the way, and the counts are wrong
     group_by(subject_ids) %>% # count up the number of distinct classification IDs
     mutate(., num_class = n_distinct(classification_id)) %>% #because there will be >1 row per classification_id if >1 spp
     arrange(., subject_ids, classification_id) 
data %>% View

# First, Identify the number of species in each subject by taking the median number of species reported across all volunteers. 
# This has to clean up times when volunteers submitted multiple classifications for a given species.

########### CLEAN UP MULTIPLE VOTES PER USER ###############
#number of different species should match the number of submissions per user
check_spp_counts <- data %>% 
     group_by(subject_ids, classification_id) %>% 
     mutate(., num_species = n_distinct(choice), check_num_spp = n()) 

# take a peek at the bad counts - these can nicely be handled though without affecting the good ones
bad_counts <- check_spp_counts %>% filter(., num_species != check_num_spp) 

if(dim(bad_counts)[1] > 0) {
     # need to figure out how to merge the different column groups, or else this will break.
     cleaned_classifications <- check_spp_counts %>% 
          select(., -check_num_spp) %>%
          # groups by everything that should be distinct - good classifications will have one row per spp
          group_by(., subject_ids, classification_id, num_class, num_species, choice) %>% 
          summarise_all(., sum) # adds up counts for duplicates of spp
} else {
     cleaned_classifications <- check_spp_counts
}


#double check...
check <- cleaned_classifications %>% 
     group_by(subject_ids, classification_id) %>% 
     mutate(., test_sp1 = n_distinct(choice), test_sp2 = n()) %>%
     filter(., test_sp1 != test_sp2) %>% nrow() %>% as.numeric() 
ifelse(check > 0, "You've got duplicates, dammit", "no more dupes!!")

# now we have a cleaned raw classification file!! # let's aggregate the number of species in a subject
# for a given subject, we take the number of species in the image as the median number of species reported, rounded up

# Calculate subject-level metrics
cleaned_classifications %<>%
     group_by(., subject_ids) %>%
     mutate(., num_votes = n(), # if a  user ids >1 spp, there will be more votes than classifications
            num_class_check = n_distinct(classification_id), #should be the same as num_class
            agg_num_species = round(median(num_species), 0), #aggregate species count, which is median rounded up
            diff_species = n_distinct(choice)) # count the total number of different species reported by different users

View(cleaned_classifications %>% arrange(., -agg_num_species))

# double check that there aren't miscounted classification numbers
cleaned_classifications %>% filter(., num_class != num_class_check) %>% nrow


### For each species, aggregate counts and behavior votes. ###
# okay, so there's a difference between the proportion of VOTES and the proportion of classifications. 
# If some users ID >1 species in a single species image, there will be more votes than classifications. 
# The opposite is true for when some users only ID 1 species in a multi-species image.

#Need to Identify behavior columns, how many columns, etc. Maybe characterize different types of columns that should be treated differently?
howmany_column <- "how_many"
behavior_columns <- c("MVNG", "RSTNG", "STNDNG", "TNG")
yesno_columns <- c("young", "horns")

# Calculate the proportion of T from a list of T/F/NA. Should work on non-required q's as well.

calc_prop <- function(x, NA_action = "non_answer") {
     #NA_action can be non_answer or zero, indicating how NAs should be treated. By default, they are treated as non_answers
     # sum(x)/length(x)  
     
     if (NA_action == "non_answer") {
          prop<- sum(x[!is.na(x)])/length(x[!is.na(x)]) # Remove NAs from both sum and length
          prop <- ifelse(is.finite(prop), prop, NA)          
     } else if (NA_action == "zero") {
          prop<- sum(x, na.rm = T)/length(x) #NAs count towards total length, but not towards the sum of 1s.
     }
     
}

# Calculating the proportion of "YES" for non-required YES/NO questions
calc_yes <- function(x, yes = c("YES", "Yes", "yes", "Y", "y", "S", "s", "YS", "ys"), NA_action = "non_answer") { 
     #treats NAs as non answers instead of zeros.
     #yes votes are anything in c("YES", "yes", "Y", "y", "S")
     if (NA_action == "non_answer") {
          prop<- length(x[x %in% yes])/length(x[!is.na(x)])
          prop <- ifelse(is.finite(prop), prop, NA)          
     } else if (NA_action == "zero") {
          prop<- length(x[x %in% yes])/length(x)
     }

}

#this provides one row per species ID per classification. We actually don't really need all the grouping variables... could just pull them apart and save for later.
grouped_classifications <- cleaned_classifications %>% 
     select(., -num_species, -num_class_check) %>% # these aren't relevant
     group_by(., subject_ids, num_class, num_votes, agg_num_species, diff_species, choice) # fields at subject level or higher

#Tally the votes for each species ID'd within a subject
species_votes <- grouped_classifications %>% 
     # for every species within a subject, aggregate votes.
     summarise(., votes = n_distinct(classification_id)) %>% #count up the number of votes per species choice
     mutate(propvote = votes/sum(votes), #calculate proportion of votes for this species
            propclass = votes/num_class) #calculate proportion of classifications for this species

# Aggregate counts (how many)
howmany_votes <- grouped_classifications  %>%
     summarise_at(., .cols = howmany_column, funs(med_count = median, min_count = min, max_count = max))

# Tally votes for the different behaviors for each species. # Generalize for multi-answer questions??
behaviors_votes <- grouped_classifications %>% 
     summarise_at(., .cols = behavior_columns, funs(calc_prop))

# Tally votes for factor questions with single answers
question_votes <- grouped_classifications %>% 
     summarise_at(., .cols = yesno_columns, funs(calc_yes))


grouped_classifications %>% 
     summarise(., horns_yes = calc_yes(horns, NA_action = "non_answer"))


# Okay, so the full dataset has all of the aggregate votes per species. The only thing left is to select the top n species for each subject.
all_data <- species_votes %>% full_join(howmany_votes) %>% full_join(., question_votes) %>% full_join(., behaviors_votes)


########### CHOOSE ONLY CONSENSUS SPECIES AND CLEAN UP DATA ##############
#full_dataset <- read.csv(file = "data/jdata-flattened-testing-ties.csv")

choose_top_species <- function(aggregated_data) {
     most_species <- max(aggregated_data$agg_num_species)
     out <- list()
     
     for (i in 1:most_species) {
          temp <- aggregated_data %>% ungroup(.) %>%
               filter(., agg_num_species == i) %>% # filter to i number of species
               group_by(., subject_ids) %>%
               top_n(n = i, wt = votes) %>% #just select top i species based on vote
               mutate(., consensus_species = choice) %>% #add this as the consensus species column
               mutate(., resolve = ifelse(n() == i, "ok", "tie")) %>% #if more than i answers per subject ID, it's a tie. this works when i >1!!!!
               top_n(n = i, wt = choice) #take the last value (or last alphabetically)
          out[[i]] <- temp 
     }
     
     consensus_data <- do.call(what = rbind, args = out) %>% 
          arrange(., subject_ids)
     return(consensus_data)
}

final_dat <- clean_up_consensus_data(consensus_dataset = consensus_data, behavior_cols = behavior_columns)


write.csv(final_dat, file = "data/wildG_aggregation.csv")
