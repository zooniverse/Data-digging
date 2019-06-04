###Tom Hart, April 2019

  ### Density Mapping and Counting Script - R code to generate 'Pengbot Density Maps' and 'Pengbot Counts' files ###

### The input files for this script are 'Pengbot Out Files' (see associated paper, and https://www.robots.ox.ac.uk/~vgg/data/penguins/, for details).

## Clear the work environment.
rm(list=ls(all=TRUE))

## Install the required packages - grid, jpeg and R.matlab (these are needed to read in MATLAB files and plot JPEGS).
## Package installation is only required the first time the script is run (although updates may be necessary).
## Install.packages(c("grid", "jpeg", "R.matlab", dependencies = TRUE))

library(grid)
library(jpeg)
library(R.matlab) 

## Set up a function to rotate the matrix 180 degrees when plotting. This ensures that the density map image corresponds 
## to the raw time-lapse image. Thanks to Matthew Lundberg via Stack Overflow.
rotate <- function(x) t(apply(x, 2, rev))

## Assign the camera name (e.g. 'GEORa'), and set up paths (for reading and writing files).
## Remember to create nested directories for the density maps to be written to (i.e. Pengbot_Density_Maps -> GEORa_pengbot_density_maps)
cameraname<-"GEORa"
path<-"C:/EXAMPLE_DIRECTORY/Pengbot_Out/"
savepath<-"C:/EXAMPLE_DIRECTORY/Pengbot_Density_Maps/"

## List all the files in the 'Pengbot_Out' folder; create read and write list.
filenames<-list.files(paste0(path, cameraname, "_pengbot_out/"))
filenames2<-paste0(path, cameraname, "_pengbot_out/", filenames)
savefiles<- paste0(savepath, cameraname, "_pengbot_density_maps/", filenames)
savefiles<-gsub(".mat", ".jpg", savefiles)
aspect<-0.75

## Create a loop to plot and count the penguin density values across the whole image. Values for nrow and ncol may need
## to be changed depending on image dimensions (in number of pixels); 2048x1536 is the standard for Penguin Watch
## images (there are also a number of 1920x1080 images; the dimensions should always be checked).

npeng<-NULL

  for (i in 1:(length(filenames)+1)){
  matl<-readMat(filenames2[i])
  dens<-as.matrix(matl$density, nrow = 1536, ncol = 2048, byrow = TRUE)
  dens2<-rotate(dens)
  npeng[i]<-sum(dens)
  jpeg(paste(savefiles[i]), width = 1000, height = 1000*aspect) 
  par(mar=c(0, 0, 0, 0))
  image(dens2, useRaster=TRUE, axes=FALSE, col = heat.colors(12)) # the colour palette can be altered as desired
  dev.off() 
}

## Create a file of Pengbot counts
imageid<-gsub(".mat", "", filenames)
pengbotout<-data.frame(imageid,npeng)
colnames(pengbotout) <- c("imageid", "count")
write.table(pengbotout, file=paste0(savepath, cameraname, "_pengbot_density_maps/", cameraname, "_pengbot_count.csv"), row.names = FALSE, sep=",")
