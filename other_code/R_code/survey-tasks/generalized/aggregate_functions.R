check_dups <- function(dat) {
     # This function groups by subject and classification ID (which is per user/classification), 
     # then checks whether the number of unique species == the number of submissions. 
     # So, if a person selects lion & zebra, num_species and check_num_species will both = 2. 
     # If a person selects lion, 1, standing and lion, 1, sitting, then num_species = 1 and check_num_species = 2.
     # Note that this error will not be possible in future projects.
     # Also note that we can't actually combine answers in a generalized way, 
     # because "how many" is actually categorical and the values differ for all projects.
     bad_counts <- dat %>% 
          group_by(subject_ids, classification_id) %>% 
          mutate(., num_species = n_distinct(choice), check_num_spp = n()) %>%
          filter(., num_species != check_num_spp) 
     check <- bad_counts %>% nrow() %>% as.numeric()
     
     if(check > 0) {
          print("You've got duplicates, dammit")
          return(bad_counts)
     } else if(check == 0) {
          print("You've got no duplicates! Well done!")
     }
}





          
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

# Calculating the proportion of "YES" for non-required YES/NO questions. Need to also do this for general single-answer questions
calc_yes <- function(x, yes = c("YES", "Yes", "yes", "Y", "y", "S", "s", "YS", "ys"), NA_action = "non_answer") { 
     # treats NAs as non answers instead of zeros.
     # yes votes are anything in c("YES", "Yes", "yes", "Y", "y", "S", "s", "YS", "ys"), for various reasons. 
     # projects can specify alternative yes answers, such as "hellz yes" for "for shizzle" if they have such non-standard values.
     if (NA_action == "non_answer") {
          prop<- length(x[x %in% yes])/length(x[!is.na(x)])
          prop <- ifelse(is.finite(prop), prop, NA)          
     } else if (NA_action == "zero") {
          prop<- length(x[x %in% yes])/length(x)
     }
     
}

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