### Tom Hart and Fiona M. Jones
                                ### Narwhal Script - R code to create a Narwhal File ###

## Narwhal Files provide count data for adults, chicks and eggs, nearest neighbour distances (and change in nearest
## neighbour distance between the ith and i-1th image) for adults and chicks, and metadata, per image.
## See corresponding paper for more information. 
## Required files:
## 1) 'Kraken Files' (Data Citation 2), generated using the Kraken Script.
## See the corresponding paper for more information about these file types.


## Clear the work environment.
rm(list=ls(all=TRUE))

## Install the "spatstat" package (if not already installed); this need only be done once.
#install.packages("spatstat", dependencies = TRUE)

## Load the "spatstat" package (this will be used for nearest neighbour distance calculations).
library(spatstat)

## Assign the camera name, e.g. 'GEORa'.
cameraname<-"GEORa"

## Read in the 'Kraken File' (Data Citation 2) associated with the camera of interest, and view the top rows.
sitefile<-paste0("C:/EXAMPLE_DIRECTORY/Kraken_Files/", cameraname, "_kraken.csv")
site<-read.table(paste(sitefile), sep=",", header=TRUE)
head(site)

## Assign image names to 'imageid'.
imageid<-levels(as.factor(site$name))

## Set up a list of variables we wish to calculate for each image (see associated paper for an explanation of each variable).

adultndout<- NULL                  ## adult nearest neighbour distance (nnd)
adultsdndout<- NULL                ## adult std dev nnd
chickndout<- NULL                  ## chick nnd
chicksdndout<- NULL                ## chick std dev nnd
chick2ndout<- NULL                 ## chick 2nd nnd (since the first nearest neighbour is likely to be its sibling in the nest)
chicksd2ndout<- NULL               ## chick std dev 2nd nnd
nadults<- NULL                     ## number of adults P>0.5*
nchicks<- NULL                     ## number of chicks P>0.5*
neggs<- NULL                       ## number of eggs P>0.5*    
meanchangeadult<- NULL             ## mean distance between each adult [j] in image [i] and the nearest adult (likely itself) in image [i-1] (shows movement) 
meanchangechick<- NULL             ## mean distance between each chick [k] in image [i] and the nearest chick (likely itself) in image [i-1] (shows movement) 
tempf<- NULL                       ## temperature in Fahrenheit recorded by the camera
lunar_phase<- NULL                 ## lunar phase recorded by the camera
datetime<- NULL                    ## date and time information recorded by the camera
URL<- NULL                         ## URL link to thumbnail of image

## This script assumes a threshold probability level of P>0.5, in line with the probability value employed in a technical validation of the
## method (see Jones et al. (2018); DOI: 10.1038/sdata.2018.124). The value can be increased to heighten the filtering threshold, meaning
## fewer 'consensus clicks' would be included. Decreasing the threshold below P>0.5 will lead to pseudoreplication; for
## example, if probability_of_adult = 0.5 and probability_of_chick = 0.5 for the same individual, and a threshold of
## P>=0.5 was implemented, the individual would be counted twice - once as an adult and once as a chick.
## The use of P values may not always be relevant - it will depend on the type of clustering algorithm used.

## Use a subset of the data first to check the code is working; e.g.
# for i in 3:100{

### Run a loop to calculate the above variables for the current dataset.


## Start with image 2 (change in nnd cannot be calculated for image 1).
for(i in 2:length(imageid)){

    x<-imageid[i] # identify the current image by name
    current<-site[which(site$name==paste(x, sep=",")),] # select the data for the current image as a subset of the whole dataframe
    datetime[i]<-as.character(current$datetime[1])
    tempf[i]<-current$temperature_f[1]
    lunar_phase[i]<-as.character(current$lunar_phase[1])     
    URL[i]<-as.character(current$URL[1])
 
## Subset individuals of interest (i.e. P>0.5), set up coordinates for nnd calculations, and generate counts.    
    
    currentadult<-current[which(current$probability_of_adult>0.5),] # select out only the adult 'consensus clicks' with adult P>0.5 for the current image
    currentadultxy<-data.frame(currentadult$x_centre, currentadult$y_centre) # create a data frame of adult x & y coordinates within the image
    currentchick<-current[which(current$probability_of_chick>0.5),] # select out only the chick 'consensus clicks' with chick P>0.5 for the current image
    currentchickxy<-data.frame(currentchick$x_centre, currentchick$y_centre) # create a data frame of chick x & y coordinates within the image
    currentegg<-current[which(current$probability_of_egg>0.5),] # select out only the egg 'consensus clicks' with egg P>0.5 for the current image
    nadults[i]<-length(currentadult[,1]) # calculate the number of adults in the current image with P>0.5
    nchicks[i]<-length(currentchick[,1]) # calculate the number of chicks in the current image with P>0.5
    neggs[i]<-length(currentegg[,1]) # calculate the number of eggs in the current image with P>0.5
   
## Calculate mean average nnd and standard deviations of nnd.
    
    adultndout[i]<-mean(nndist(currentadultxy)) # calculate the mean nnd for adults
    adultsdndout[i]<-sd(nndist(currentadultxy)) # calculate the standard deviation of adult nnd
    chickndout[i]<-mean(nndist(currentchickxy)) # calculate the mean nnd for chicks
    chicksdndout[i]<-sd(nndist(currentchickxy)) # calculate the standard deviation of chick nnd
    chick2ndout[i]<-mean(nndist(currentchickxy, k=2)) # calculate mean chick 2nd nnd (since the first nearest neighbour is likely to be a sibling in the nest)
    chicksd2ndout[i]<-sd(nndist(currentchickxy, k=2)) # calculate the standard deviation of chick 2nd nnd


## The objective of this section is to detect movement of adults by calculating the distance between each adult [j] in image [i] and its nearest neighbour (likely
## itself) in image [i-1].
## This is also calculated for chicks.
    
    y<-imageid[i-1]  # as for x above, but this identifies the previous image (i-1)
    prev<-site[which(site$name==paste(y, sep=",")),] # subset out a data frame of just the previous image (i-1)
    prevadult<-prev[which(prev$probability_of_adult>0.5),] # subset out a data frame of adults with P>0.5 in the previous image (i-1)
    prevadultxy<-data.frame(prevadult$x_centre, prevadult$y_centre) # create a data frame of adult x & y coordinates within this image
    prevchick<-prev[which(prev$probability_of_chick>0.5),] # subset out a data frame of chicks with P>0.5 in the previous image (i-1)
    prevchickxy<-data.frame(prevchick$x_centre, prevchick$y_centre) # create a data frame of chick x & y coordinates within this image

## Set up the previous image nnd variables. 
prevadultndout<- NULL
prevchickndout<- NULL

## Run a loop to calculate the nnd for each adult [j] in image [i], in image [i-1].
for (j in 1:length(currentadultxy[,1])){ 
  
  currentadultx<-currentadultxy$currentadult.x_centre[j] # identifies the jth adult of interest, x coordinate
  currentadulty<-currentadultxy$currentadult.y_centre[j] # identifies the jth adult of interest, y coordinate
  prevadultx<-c(currentadultx, prevadult$x_centre) # appends the x coordinate of the current adult of interest to the adult x coordinates in the previous image [i-1]
  prevadulty<-c(currentadulty, prevadult$y_centre) # appends the y coordinate of the current adult of interest to the adult y coordinates in the previous image [i-1]
  prevadultxy<-data.frame(prevadultx, prevadulty) # makes a data frame of the x & y coordinates of the adults in the previous image [i-1] and the adult of interest in the current image

  temp<- NULL # set up a temporary variable to store adult nnds
  ifelse(prevadultxy$prevadultx[1]=="NA", temp[1]<-NA, temp<-nndist(prevadultxy)) # logic statement; if there are no adults in the previous image, record NA. Otherwise calculate the nnd of the prevadultxy dataframe.
  prevadultndout[j]<-temp[1] # only record the nnd for the adult of interest [j]. Prevadultndout will become a vector of the distance between each adult of interest and the nearest neighbour adult in the previous image (which will likely be itself).
  }


## Run a loop to calculate the nnd for each chick [k] in image [i], in image [i-1].
for (k in 1:length(currentchickxy[,1])){
  
  currentchickx<-currentchickxy$currentchick.x_centre[k]  # identifies the kth chick of interest, x coordinate
  currentchicky<-currentchickxy$currentchick.y_centre[k]  # identifies the kth chick of interest, y coordinate
  prevchickx<-c(currentchickx, prevchick$x_centre) # appends the x coordinate of the current chick of interest to the chick x coordinates in the previous image [i-1]
  prevchicky<-c(currentchicky, prevchick$y_centre) # appends the y coordinate of the current chick of interest to the chick y coordinates in the previous image [i-1]
  prevchickxy<-data.frame(prevchickx, prevchicky) # makes a data frame of the x & y coordinates of the chicks in the previous image [i-1] plus the chick of interest in the current image
  
  temp2<-NULL # sets up a temporary variable to store chick nnds
  ifelse(prevchickxy$prevchickx[1]=="NA", temp2[1]<-NA, temp2<-nndist(prevchickxy)) # logic statement; if there are no chicks in the previous image, record NA. Otherwise calculate the nnd of the prevchickxy dataframe.
  prevchickndout[k]<-temp2[1] # only record the nnd for the chick of interest [k]. Prevchickndout will become a vector of the distance between each chick of interest and the nearest neighbour chick in the previous image (which will likely be itself).
}  

meanchangeadult[i]<-mean(prevadultndout)
meanchangechick[i]<-mean(prevchickndout) 

}

## Calculate temperature (rounded to 2dp) in degrees Celsius from the Fahrenheit values, and assign to 'tempc'.
tempc<-(tempf-32)/1.8
tempc<- round(tempc,2)

## Create a data frame of all variables.
narwhal<-data.frame(imageid, datetime, nadults, nchicks, neggs, adultndout, 
                    adultsdndout, chickndout, chicksdndout, chick2ndout, chicksd2ndout,
                    meanchangeadult, meanchangechick, tempf, tempc, lunar_phase, URL)


## Save the data frame as a Narwhal File.
path<-paste0("C:/EXAMPLE_DIRECTORY/Narwhal_files/")
write.csv(narwhal, paste0(path, cameraname, "_narwhal.csv"), row.names = FALSE)

## Note that there may be warnings, even if a successful file has been created. Check these to determine the 
## nature of the warnings.
