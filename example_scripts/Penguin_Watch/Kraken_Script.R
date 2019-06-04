### Fiona M. Jones
                                ### Kraken Script - R code to create a Kraken File ###

## Kraken Files provide filtered 'consensus click' data and metadata for each Penguin Watch image
## - see corresponding paper for more information. 
## Required files:
## 1) 'Consensus click data' (Data Citation 1; DOI: 10.5061/dryad.vv36g)
## - see Jones et al., 2018 (DOI: 10.1038/sdata.2018.124) for a detailed explanation of 'consensus click' files.
## 2) 'PW_manifest' (Data Citation 2) - see corresponding paper for more information.


## Clear the work environment. 
rm(list=ls(all=TRUE))

## Assign the camera of interest to 'camera', e.g.'GEORa'.
camera<- "GEORa"

## Assign the directory you wish to store output files in to 'savepath'.
savepath<- "C:/EXAMPLE_DIRECTORY/Kraken_Files/"

## Read in the 'consensus clicks' for the camera of interest. These can be found at DOI: 10.5061/dryad.vv36g (Data Citation 1).
cam<- read.table("C:/EXAMPLE_DIRECTORY/Consensus_clicks_replacement/GEORa2013a_concl.csv", sep=",", header=TRUE)

## If you wish to process multiple files associated with a camera, read them in as cam2, cam3 etc., and use the 'rbind' command to join them.
## rbind(cam, cam2, cam3...camn) 

cam2<- read.table ("C:/EXAMPLE_DIRECTORY/Consensus_clicks_replacement/GEORa2013b_concl.csv", sep=",", header=TRUE)

cam<- rbind(cam, cam2) 

## Extract the adult 'consensus click' data (probability_of_adult > 0.5) where the number of markings (num_markings) is greater than x (here x=3). 
## Select required columns.
adults<- subset(cam, probability_of_adult > 0.5 & num_markings > 3, select = c(name, probability_of_adult, probability_of_chick, probability_of_egg, num_markings, x_centre, y_centre))

## Extract the chick (probability_of_chick > 0.5) and egg (probability_of_egg > 0.5) 'consensus click' data where the number of markings (num_markings) is greater than x (here x=1).
## Select required columns.
chicks<- subset(cam, probability_of_chick > 0.5 & num_markings > 1, select = c(name, probability_of_adult, probability_of_chick, probability_of_egg, num_markings, x_centre, y_centre)) 
eggs<- subset(cam, probability_of_egg > 0.5 & num_markings > 1, select = c(name, probability_of_adult, probability_of_chick, probability_of_egg, num_markings, x_centre, y_centre)) 


## Bind the adult, chick and egg data together, and order by image name.
newdata<- rbind(adults, chicks, eggs)
newdata<- newdata[order(newdata$name),] 

## Remove the object 'cam' (and 'cam2' etc. if necessary).
rm(cam)
rm(cam2)

## Shorten the image names (remove .csv).
newdata$name<- gsub(pattern= ".csv", replacement ="", newdata$name)


########################

## Read in the Penguin Watch Manifest (see Data Citation 2).
manifest<- read.table("C:/EXAMPLE_DIRECTORY/PW_Manifest.csv", sep="," , header=TRUE)

## Select only those metadata associated with the camera of interest; view first rows of the extraction (including column headers).
lis<- grep(paste0(camera), manifest$name)
mani<- manifest[lis,]
head(mani)

## Remove any unrequired variables. 
mani$zooniverse_id<- NULL
mani$path<- NULL
mani$classification_count<- NULL
mani$state<- NULL

## Check the metadata extraction.
head(mani)
tail(mani)

## Reorder columns if necessary, e.g:
#mani<- mani[,c(1,3,4,2,5)]

## Ensure names are ordered alphabetically and by number.
mani<- mani[order(mani$name),] 

########################

## Combine the filtered 'consensus clicks' with 'mani'.  
## Since the files are different lengths (and we want to include data for all images), it is necessary to merge using 'all.x = TRUE, all.y = TRUE'.
comb_data<- merge(newdata, mani, by.x = "name", by.y = "name", all.x = TRUE, all.y = TRUE)

## Write the dataframe to a csv file.
write.csv(comb_data, paste0(savepath, camera, "_kraken.csv"), row.names=FALSE)
