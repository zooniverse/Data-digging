This script is written in Python 3.6.2.  It requires a number of Python packages

Panoptes client from http://panoptes-python-client.readthedocs.io/en/latest/user_guide.html#installation

Pillow from https://pillow.readthedocs.io/en/5.0.0/installation.html

requests from http://docs.python-requests.org/en/master/

These all can be installed flawlessly via the Pycharm Edu package installer as well. (Found under Settings, Project, Project Interpreter, Install more Packages)

To use This script, the easiest way is to create a new directory where you want to download the subject images to, then copy this script to that directory, and run it from there.

The script uses Environmental variables stored in your Operating System to log in to zooniverse. This is actually only necessary if the subject set you wish to download is linked to a Private project. If the project is Public you can delete line 10 entirely. For Windows 10 Environmental variables are set as follows: ControlPanel > System and Security > System > Advanced System setting (on left) > Environmental Variables (lower right) > User Variables (upper pane) - New.  Enter User_name as the Variable name, and your zooniverse name as the value, then click OK. Repeat for Variable name Password, and your zooniverse password as the value, then click Ok.  At this point the list of User variables should show User_name and Password in the list with your zooniverse log in credentials as the respective values.  Click Ok at bottom and restart your compurter to update the environmental variables. 

You could also modify line 10 hardcode your credentials as follows:
````
Panoptes.connect(username='User_name', password='Password')
````
where User_name and Password are replaced in the code with your zooniverse credentials - but in this case you must secure the code to protect your password.

The script asks for the subject set id number.  If the set id has been deleted, it reports it as not found.  Note: it appears subject sets other than those for your project can be downloaded, so be careful you have selected the correct one!

The script then queries the subject set adding the all the members to a list. The script reports the number of subjects in the subject set ready to download. This can take a few minutes for a large subject set!!!

Once that task is finished, the script asks for the path of the directory to download to, with a shortcut for the current working directory.

Once that input has been tested as a valid location the script proceed to acquire each image and download it to the local directory.  The script attempts to retain any exif data the subject has, though this may not be as complete as the original since some exif data can be lost during the upload process when the subject was created. 

The file_name is derived from the subject metadata.  Subjects with no Filename attribute will be saved as subject_number.jpg.  Note Filename is the default metadata field for images uploaded with either the subject_uploader.py in this repository or the project uploader using auto upload.  If your subjects have some other metadata fields you wish to use for the file name (eg 'file_name')you will need to modify this section.

If a file of the same name exists in the directory as a file prepared for download, the download does not proceed for that subject - it is simply skipped. Thus if the process is interupted it can be restarted at any time with minimal loss of time and effort. 
