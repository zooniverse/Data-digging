## Subject_uploader

There are two versions of this script.  subject_uploader.py is written in Python 3.6, while subject_uploader_2,py is written in Python 2.7  Both have been tested with small subject sets only, but with a stable internet connection should work fine for larger sets.  In any case error handling should carry the process through any errors and the final part of the script produces a file with the filenames of the subjects that were successfully uploaded for verification.

Both scripts work the same way.  
First the script connects with the Panoptes Client using your zooiniverse User_name and Password. These have to be set as environmental variables for your computer using your OS.  Alternately these can be hardcoded in the script if you keep it private enough.  The project slug "pmason/fossiltrainer" must be replaced to match that for your project, and you must have colaborator or owner status on the project.

Second, a minimal UI asks for the path to the image files to be uploaded.  The script will find all image files in that directory and attempt to upload them. It is important that the directory only contain image files you want uploaded.  Non-image files are ignored so it is quite practical to place a copy of the script in the directory and run everything from that directory as the current working directory.

Next the UI asks for the display_name for the subject set you want to create or use.  The script will search for the subject set and prepare to add to it if it exists or create it if new.

There is then a confirmation step where the number of files to upload and where they are to be added can be verified before proceeding.

Once that is done the script proceeds to determine what files if any are in the subject set already.  It then attempts to upload any files that are naot already uploaded to the subject set.  This can take some time.  The file names are displayed as each file upload is completed and the subject has been linked to the subject set.

The final step queries the subject set directly and produces a file containing the filenames of all the subjects in the subject set at the end of the uploading process.  This can be used, along with the subject set counts, to verify all the subjects were uploaded correctly.
