#Processes a CSV file downloaded from 'Steller Watch'. Year must be in the format Y-M-D. top100 only reads the first 100 rows from the CSV for testing.

#The columns must include 'created_at', 'workflow_version', 'annotations' (a JSON value with a 'task', 'task_label', and 'value'), and 'subject_ids' (a JSON value structures like '{subject_id:{retired:...,Filename:...}}').

#returns a structure like this:
#   named list :
#   [
#     workflow_id 1 :
#       [
#         task T0 : data.frame,
#         task T1 : data.frame,
#         ...
#       ],
#     workflow_id 2 :
#       [
#         task T0: data.frame,
#         task T1 : data.frame,
#         ...
#       ],
#     ...
#   ]
#colnames(data.frame) = subject_ids, photo_name, frame_num, count of task answer 1, count of task answer 2, ...

ProcessCSV <- function(fileName, minDate, maxDate, top100) {
  if (missing(top100) || !top100) {
    df <- read.csv(file=fileName)
  } else {
    df <- read.csv(file=fileName, nrows=100)
  }
  if (!require("jsonlite")) {
    install.packages("jsonlite")
    require("jsonlite")
  }
  if (!require("dplyr")) {
    install.packages("dplyr")
    require("dplyr")
  }
  #You can use reshape instead, but have to change melt() parameters.
  if (!require("reshape2")) {
    install.packages("reshape2")
    require("reshape2")
  }
  #subset by created_at date range
  if (!missing(minDate) && !missing(maxDate)) {
    df <- subset(df, as.Date(created_at) >= as.Date(minDate) & as.Date(created_at) <= as.Date(maxDate))
  } else if (!missing(minDate)) {
    df <- subset(df, as.Date(created_at) >= as.Date(minDate))
  } else if (!missing(maxDate)) {
    df <- subset(df, as.Date(created_at) <= as.Date(maxDate))
  }
  #Collapse df with frequencies
  df <- df %>% group_by(annotations, workflow_id, workflow_name, workflow_version, subject_ids, subject_data) %>% summarise(count = n())
  #transpose tasks so that task number is column name, and concatenate values from a single task.
  #Had trouble doing this with a mutate() or apply() because of dynamic column names.
  for(i in 1:nrow(df)) {
    ann <- fromJSON(as.character(df[[i,'annotations']]))
    sub <- fromJSON(as.character(df[[i,'subject_data']]))[[1]]
    #NA to replace NULLs otherwise you get a replacement has length zero error
    photoname <- c(sub[['#ImageName']], sub[['#image_name']], sub[['Filename']], sub[['#Filename']], NA)
    imagenum <- c(sub[['#Frame']], NA)
    df[i,'photo_name'] <- photoname[which(!is.null(photoname))[1]]
    df[i,'frame_num'] <- imagenum[which(!is.null(imagenum))[1]]
    for(j in 1:nrow(ann)) {
      task <- ann[j,'task']
      value <- paste(unlist(ann[j,'value']), collapse = ', ')
      df[i,task] <- value
    }
  }
  #drop annotations and subject_data from output
  df <- df[, !(names(df) %in% c("annotations", "subject_data"))]
  #Have to convert to data.frame because dplyr outputs it as a tibble which cannot be passed into melt()
  df <- data.frame(df, stringsAsFactors = TRUE)
  #unpivot
  df <- melt(df, id = c("subject_ids", "photo_name", "frame_num", "workflow_id", "workflow_name", "workflow_version", "count"), na.rm = FALSE)
  #Re-count
  df <- df %>% group_by(subject_ids, photo_name, frame_num, workflow_id, workflow_name, workflow_version, variable, value) %>% summarise(count = sum(count))
  #rename columns because cast() cares about "variable" and "value", and manually setting those as parameters does not work.
  df <- rename(df, c("variable" = "task", "value" = "variable", "count" = "value"))
  #split df by workflow
  splitDF <- split(df, f = df$workflow_id)
  for (i in 1:length(splitDF)) {
    #split by task ($variable)
    splitDF[[i]] <- split(splitDF[[i]], f = splitDF[[i]]$task)
    for (k in 1:length(splitDF[[i]])) {
      #pivot tables by $variable (task answers), with summed counts
      splitDF[[i]][[k]] <- cast(splitDF[[i]][[k]], subject_ids + photo_name + frame_num ~ variable, sum)
    }
  }
  return(splitDF)
}
#Example use
result <- ProcessCSV(
    fileName = "//Nmfs/akc-nmml/Alaska/Data/Steller Sea Lion/Remote Cameras/Zooniverse/Dataexports/2_Full/steller-watch-classifications_USETHISONE.csv"
    , minDate = "2017-3-14"
    , maxDate = "2017-7-12" 
    , top100 = FALSE
  )
