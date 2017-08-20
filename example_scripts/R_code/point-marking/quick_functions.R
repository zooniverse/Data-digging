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
