##Tom Hart and Fiona Jones, with original code from Robin Freeman

##Clear the work environment
rm(list=ls())
ls()

##Call required packages
library(jpeg)
library(grid)

##Assign the camera name; a loop can be implemented if images from multiple cameras require processing:

cameras<-c("camera 1", "camera 2", "camera 3")

for (j in 1:length(cameras)){
  cameraname<-cameras[j]
  
  cameraname<-"camera 1"
  path<-"C:/Example/Path"
  
##Create new directories for the storage of renamed and resized images (here, 'Renamed images' and 'Zooniverse images', respectively):
    
  renamed<-paste(path, cameraname, "/", sep = "")
  dir.create(path=renamed, showWarnings = TRUE, recursive = FALSE, mode = "0777")
  
  zooniversed<-paste(path, cameraname, "/", sep = "")
  dir.create(path=zooniversed, showWarnings = TRUE, recursive = FALSE, mode = "0777")
  
  origindir<-paste(path, cameraname, "/", sep = "")
  copydir <-paste(path, cameraname, "/", sep = "")
  zoodir<-paste(path, cameraname, "/", sep = "")
  
##Create a list of files to copy, and copy them across to copydir:

  filestocopy <- list.files(origindir)
  
  #filestocopy<-filestocopy[2:788] # use to select specific files
  
  movelist <- paste(origindir, filestocopy, sep='')
  file.copy(from=movelist, to=copydir, copy.mode = TRUE)
  
##Run the rename script, which will automatically rename to the camera unique ID:
  
  files<-list.files(copydir)
  l<-length(files)
  
  a <- paste(copydir, files, sep='')
  nameslist<-paste(cameraname, sprintf("_%06d", 1:l, sep = ""))
  nameslist<-gsub("\\s+","",nameslist)
  b<-paste(copydir, nameslist, ".JPG", sep = "") 
  file.rename(a, b)
  
##Resize each of these images. Note, the user must consult their original image files to identify the aspect ratio, and scale accordingly. 
  
  c<-paste(zoodir, nameslist, ".JPG", sep = "") 
  
  for(i in 1:length(nameslist)) {
    currpic<-readJPEG(paste(b[i]), native=TRUE)
    
    #currpic<-readJPEG(paste(b[10]), native=TRUE)
    
    dims<-dim(currpic)          ## calculate the dimensions of currpic      
    aspect<-dims[1]/dims[2]     ## calculate the aspect ratio of currpic
    
    ## if the aspect ratio is 0.75 (as usual), proceed with resize to 1000x750. 
    ## if the aspect ratio is 0.5625 (occasional) resize to 1000x562.5
    ## if the aspect ratio does not equal either, print an error message.
    
    if(aspect == 0.75) {
      
      dw<-1000
      dh<-750
      
      jpeg(paste(c[i]), width = dw, height = dh) 
      grid.raster(currpic, width=unit(1,"npc"), height=unit(1,"npc"))
      dev.off() 
      
      
    } else if (aspect == 0.5625) {
      
      dw<-1000
      dh<-562.5
      
      jpeg(paste(c[i]), width = dw, height = dh) 
      grid.raster(currpic, width=unit(1,"npc"), height=unit(1,"npc"))
      dev.off() 
      
    } else {
      
      print("error - unrecognised aspect ratio")
      
    }
    
  }
  
  alarm()
  
##Extract the metadata from each image, and write them to a file:
  
  workdir<-paste(path, cameraname, "/", sep = "")
  setwd(workdir)
  path<-paste("F:/2016_COPY/Cameras_2016/Fiona_Images/Renamed images/", cameraname, "/", sep = "")
  
  #read in the EXIF data file for processing and renaming images
  paste(path, cameraname, sep="")
  
  
  my_cmd <- sprintf("C:\\exiftool\\exiftool.exe -T \"%s*\" > data.txt", paste(path, cameraname, sep=""))
  
  shell(my_cmd)
  
  datafile<- read.table("data.txt", sep="\t")
  head(datafile)
  
  datafile2<-NULL
  datafile2$imageid<-datafile$V2
  datafile2$datetime<-datafile$V23
  datafile2<-as.data.frame(datafile2)
  datafile2$moon<-datafile$V33
  datafile2$tempf<-datafile$V34
  datafile2$tempc<-datafile$V35
  
  levels(datafile2$moon)[levels(datafile2$moon)=="Full"] <- "full"
  levels(datafile2$moon)[levels(datafile2$moon)=="New"] <- "new"
  levels(datafile2$moon)[levels(datafile2$moon)=="New Crescent"] <- "newcres"
  levels(datafile2$moon)[levels(datafile2$moon)=="First Quarter"] <- "firstq"
  levels(datafile2$moon)[levels(datafile2$moon)=="Waxing Gibbous"] <- "waxinggib"
  levels(datafile2$moon)[levels(datafile2$moon)=="Waning Gibbous"] <- "waninggib"
  levels(datafile2$moon)[levels(datafile2$moon)=="Last Quarter"] <- "lastq"
  levels(datafile2$moon)[levels(datafile2$moon)=="Old Crescent"] <- "oldcres"
  
  #refdata<-head(datafile)
  datafile2<-data.frame(datafile2)
  head(datafile2)
  
  savepath<-paste(zooniversed, cameraname, "/", cameraname, " zoo.csv", sep = "")
  
  write.table(datafile2, savepath, sep=",", col.names=TRUE, row.names=FALSE)
  
  rm(list = c('a','b','datafile','l','files','my_cmd','path'))
  
}
  
  
  
  
  