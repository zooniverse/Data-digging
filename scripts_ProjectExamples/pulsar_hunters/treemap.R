# Forked from https://github.com/mkosmala/ZooniverseHelperScripts/blob/master/treemap.R
#
# Written by Margaret Kosmala <mkosmala@gmail.com> 2015-11-12
# Adapted from Philip Brohan's code posted 2013-05-01 to
#    Zooniverse science team group blog
# This version updates Philip's code to use the newer version
#    of the treemap package
#
# This code will create a "treemap" visualization. It is useful
# for showing the relative contributions of your users to your
# Zooniverse project. Each square represents a user and the
# size of the square is proportional to the number of
# classifications that user has done.
#
# The input is a csv file containing one column that has unique
# identifiers for each user (either an ID or username) and
# another column that indicates how many classifications each
# user has done. A column that specifies the color to make each
# user's square is optional. Each value in the color column
# should be a string in the RGB hex format "#RRGGBB".
#
# The treemap reference document is here:
# https://cran.r-project.org/web/packages/treemap/treemap.pdf


# run this once
#install.packages('treemap')

# run this all the time
library(treemap)

# ------------------
# fill this part out
# ------------------

# input file
#data_filename = 'by_user_session_stats_marking_2015-07-16_to_2015-11-12.csv'
data_filename = '/Users/vrooje/Astro/Zooniverse/pulsar-hunters-analysis/class_counts_colors.csv'

# put your column names here
unique_ids = 'user_label'
#num_of_classifications = 'nclass_user'
num_of_classifications = 'count'

# If you want to specify user colors, set this to true and provide
# the column containing the hex RGB colors
specify_colors = TRUE
user_color = 'color'
# Otherwise, set specify_colors to false
#specify_colors = FALSE

# output file
out_filename = '/Users/vrooje/Astro/Zooniverse/pulsar-hunters-analysis/pulsar_treemap_all.png'
out_title = 'Pulsar Hunters Classification Counts By User'

# ----------------------------
# now you are ready to run all
# ----------------------------

# read in file
ts = read.csv(data_filename,header=TRUE)

# create the output file
# default is PNG; change to suit your needs
png(file=out_filename,width=960,height=800)

# create the visualization
if (specify_colors) {
  treemap(ts,
          index=unique_ids,
          vSize=num_of_classifications,
          vColor=user_color,
          type="color",
          title=out_title,
          fontsize.title=25,
          position.legend="none")
} else {
   treemap(ts,
           index=unique_ids,
           vSize=num_of_classifications,
           title=out_title,
           fontsize.title=25)
}

# close the output file
dev.off()
