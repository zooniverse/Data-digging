#' ##############################
#' Code to summarise user behavior over the course of a project
#' based on a visualization by Pamela Gay. Code is written for
#' lightly post-processed data from Floating Forests (JSON is rotated
#' into being part of the main CSV to acquire start dates). Comments below
#' on different steps to help you customize for your project. 
#' Original viz from https://twitter.com/jebyrnes/status/1141921353034944512
#'
#' @author Jarrett Byrnes
#' @email jarrett.byrnes@umb.edu
#'
#' ##############################


#load libraries
library(tidyverse)
library(readr)
library(lubridate)
library(tsibble)
library(ggplot2)

#the relevant directories for data read and write
read_dir <- "../../../data/relaunch_data/level_0/"
write_fig_dir <-  "../../../figures/relaunch_viz/"

# load the data and filter to relevant
# worflow and columns - data has been processed by
# https://github.com/Irosenthal/Floating_Forests/blob/master/scripts/relaunch_data_pipeline/data_pipeline/1_separate_data_from_workflows.R
# but, in essence, you'll need a way to get classification JSON into a data table.
# The object here stored in the rds is a tibble (but will work with a data frame)

ff_data <- readRDS(str_c(read_dir, "floating_forests_classifications.rds")) %>%
  select(classification_id, user_name, user_id, started_at) %>%
  mutate(started_at =  parse_date_time(started_at, orders = "ymdHMS")) %>%
  filter(!is.na(started_at)) 

# Make data into time aware tsibble
# See https://cran.r-project.org/web/packages/tsibble/index.html
ff_data_tsbl <- ff_data %>% 
  as_tsibble(key = classification_id, index = started_at)

#get daily user summary stats
user_summary <- ff_data_tsbl %>%
  
  #first, get summary per user per week
  group_by(user_name) %>%
  index_by(year_week = as.Date(yearweek(started_at))) %>%
  summarize(classifications = n()) %>%
  ungroup() %>%
  as_tibble() %>%
  
  #now let's clean it up to make some nice order to 
  #users for the y-axis
  group_by(user_name) %>%
  mutate(min_date = min(year_week)) %>%
  ungroup() %>%
  arrange(user_name) %>%
  mutate(ord = -1*rank(min_date, ties.method = "first")) %>%
  group_by(user_name) %>%
  mutate(ord = max(ord)) %>%
  ungroup() %>%
  mutate(ord = rank(ord)) %>%
  arrange(year_week) %>%
  
  #if you sparate logged in and not logged in
  mutate(is_logged_user = ifelse(str_detect(user_name, "not-logged-in"), "Not Logged In", "Logged In")) %>%
  group_by(is_logged_user) %>%
  mutate(grouped_ord = rank(ord)) %>%
  ungroup()
  

# Plot and save!
# First, all of the data
ggplot(user_summary,
       aes(x = ord, y = year_week, size = classifications)) +
  geom_point(alpha = 0.5) +
  coord_flip() +
  theme_bw(base_size = 14) +
  theme(axis.text.y = element_blank()) +
  xlab("") + ylab("") +
  guides(size = guide_legend("Classifications\nper week"))

ggsave(str_c(write_fig_dir, "user_survivorship.jpg"))


# See logged in and not logged in
ggplot(user_summary,
       aes(x = grouped_ord, y = year_week, size = classifications)) +
  geom_point(alpha = 0.5) +
  facet_wrap(~is_logged_user) +
  coord_flip() +
  theme_bw(base_size = 14) +
  theme(axis.text.y = element_blank()) +
  xlab("") + ylab("") +
  guides(size = guide_legend("Classifications\nper week"))

ggsave(str_c(write_fig_dir, "user_survivorship_grouped.jpg"), width = 10)



# See just logged in users
ggplot(user_summary %>% filter(is_logged_user == "Logged In"),
       aes(x = grouped_ord, y = year_week, size = classifications)) +
  geom_point(alpha = 0.5) +
  coord_flip() +
  theme_bw(base_size = 14) +
  theme(axis.text.y = element_blank()) +
  xlab("") + ylab("") +
  guides(size = guide_legend("Classifications\nper week"))

ggsave(str_c(write_fig_dir, "user_survivorship_logged_in.jpg"))
