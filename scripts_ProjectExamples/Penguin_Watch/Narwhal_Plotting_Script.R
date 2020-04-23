### Tom Hart, Fiona M. Jones and Ignacio Juarez Martinez, May 2019

  ### Narwhal Plotting Script - R code to create graphs of (moving average) count data and nearest neighbour distance metrics ###

### The input files for this script are Narwhal Files (see associated paper for an explanation).
### The code produces a graph for every time-lapse image, showing the trends (up to the current image) of the following
### variables, as moving averages:
### - number of adults
### - number of chicks 
### - chick second nearest neighbour distance 
### - mean adult movement 

## Clear the work environment.   
rm(list=ls(all=TRUE))

## Install the required packages (only necessary once).
## install.packages(c("grid", "jpeg", "magick", dependencies = TRUE))
## Load the required packages.

library(grid)
library(jpeg)
library(magick)
  
## Assign the site name and camera name, e.g. 'GEORa' and 'GEORa2013'.
site<-"GEORa"
cameraname<-"GEORa2013"

## Set up a path for reading in Narwhal Files
readpath<-"C:/EXAMPLE_DIRECTORY/NARWHAL/Narwhal_Plots/"

## Read in the relevant Narwhal File and provide access to imageid levels.
narwhal<-read.table(paste0(readpath, site, "_narwhal.csv"), sep=",", header=TRUE)
imageid<-levels(as.factor(narwhal$imageid))

## Set up two moving average functions (with thanks to Matti Pastell from Stack Overflow).
## Values of n (the number of images over which an average will be calculated) can be changed as required. 
ma <- function(x,n=20){filter(x,rep(1/n,n), sides=2)}
ma2 <- function(x,n=2){filter(x,rep(1/n,n), sides=2)}

## Apply the ma function to nadults, nchicks and meanchangeadults. Apply the ma2 function to chick2ndout (these data can
## be sporadic, so a lower n value is required). The n numbers (the number of images over which a moving average is
## taken) can be altered as desired. 
manadults<-ma(narwhal$nadults)
manchicks<-ma(narwhal$nchicks)
machick2ndout<-ma2(narwhal$chick2ndout)
mameanchangeadult<-ma(narwhal$meanchangeadult)

## Calculate the range of the summary statistics, so that the axes can be appropriately scaled. This function
## finds the maximum value, and rounds it up to the nearest 10. Thanks to Abe from Stack Overflow.
## NA and Inf values are removed.
scale_func <- function(x) ceiling(max(x)/10)*10

maxadults<-max(narwhal$nadults, na.rm=TRUE)
maxadults<-scale_func(maxadults)

maxchicks<-max(narwhal$nchicks, na.rm=TRUE)
maxchicks<-scale_func(maxchicks)

chick2nnd <- narwhal$chick2ndout[which(narwhal$chick2ndout < Inf)]
maxchick_dist<-max(chick2nnd, na.rm=TRUE)
maxchick_dist<-scale_func(maxchick_dist)

movement <- narwhal$meanchangeadult[which(narwhal$meanchangeadult < Inf)]
max_mov <- max(movement, na.rm=TRUE)
max_mov <- scale_func(max_mov)

## Show the maximum values. Use them to choose the greatest value out of maxadults and maxchicks to set the y axis 
## limit for plot 1, and use maxchick_dist and max_mov to draw the axes for plots 2 and 3, respectively).
## If a value of -Inf is displayed (because all values are NA in the Narwhal File), set the limit manually below.

maxadults
maxchicks
maxchick_dist
max_mov

## Change the datetime formatting (so axes can be labelled correctly).
narwhal$datetime<-strptime(narwhal$datetime, format = "%Y:%m:%d %H:%M:%S", tz="GMT")

## Create a loop which reads in the current image and plots it above three summary graphs:
## 1) Number of adults and number of chicks (moving average)
## 2) Chick second nearest neighbour distance (moving average)
## 3) Adult movement (moving average)
## We start at '2' because change cannot be calculated for the first image.

 for (i in 2:length(imageid)){

## Or plot the graph for a single image (e.g the last image in the dataset).
 ##i <- 407
  
  ## Assign paths for reading and writing files.
  path<-paste0(readpath, cameraname, "/", imageid[i], ".JPG")
  img<-image_read(path)
  savename<-paste0(readpath, cameraname, "_plots/", imageid[i], ".JPG")
  jpeg(savename, width = 1000, height = 1000)
  
  ## Plot the time-lapse image, and add graph layout (i.e. 6 columns, 11 rows - to get the correct size and spacing -
  ## filled with four different plot types).
  ## Thanks to Batanichek and Molx from Stack Overflow for their posts about layout(matrix).
  layout(matrix(c(1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
                  1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
                  0,2,2,2,2,0,0,2,2,2,2,0,
                  0,3,3,3,3,0,0,3,3,3,3,0,
                  0,4,4,4,4,0,0,4,4,4,4,0), nrow = 11, ncol = 6, byrow = TRUE))
  par(mar=c(0.3,5,5,5)) ## Set the size of margins
  plot(img)
  ticklen<- c(0.1) ## tick mark length
  

  ## Plot a graph for nadults and nchicks (moving average):
  
  par(mar=c(2,5,0.5,5))
  plot(narwhal$datetime, manadults, type="n", xaxt="n", cex.axis=1.75, col.axis="red",
  ylab="No. of adults", col.lab="red", cex.lab=2, ylim=c(0,maxadults))
  axis(4, cex.axis=1.75, col.axis="green", ylim=c(0,maxadults))
  mtext("No. of chicks", 4, col="green", cex=1.4, line=2.75)
  lines(narwhal$datetime[1:i], manadults[1:i], col="red", lty=1, lwd=3)
  lines(narwhal$datetime[1:i], manchicks[1:i], col="green", lty=2, lwd=3)
  ## Add optional legend (axes are colour coded already).
  ## legend("topright", inset = 0.053, legend = c("Adults", "Chicks"), col = c("red", "green"), lty=1:2, cex=1.75)
  ## Add start, middle and end date to the x axis.
  r2<-c(narwhal$datetime[2], narwhal$datetime[nrow(narwhal)/2], narwhal$datetime[nrow(narwhal)])
  axis.POSIXct(1, at=r2, format="%d-%b-%y", cex.axis=2)
  
  
  ## Plot a second graph for chick second nearest neighbour distances (moving average): 
  
  par(mar=c(2,5,0.8,5))
  plot(narwhal$datetime, machick2ndout, type="n",  xaxt="n", cex.axis=1.75,
  ylab="Chick 2nd nnd (px)", col.lab="black", cex.lab=2, ylim=c(0,maxchick_dist)) # or ylim can be set manually, e.g. ylim=c(0,30) 
  lines(narwhal$datetime[1:i], machick2ndout[1:i], col="blue", lty=1, lwd=3)
  axis.POSIXct(1, at=r2, format="%d-%b-%y", cex.axis=2)
  axis.POSIXct(3, at=r2, labels=F)
  
  ## Plot a third graph for adult movement (moving average):
  
  par(mar=c(0.5,5,0.8,5))
  plot(narwhal$datetime, mameanchangeadult, type="n", xaxt="n", cex.axis = 1.75,
  ylab="Ad. movement (px)", xlab="", col.lab="black", cex.lab=2, ylim=c(0,max_mov))
  lines(narwhal$datetime[1:i], mameanchangeadult[1:i], col="orange", lty=1, lwd=3)
  axis.POSIXct(3, at = r2, labels = F)
  
  
  dev.off() 
  
}
