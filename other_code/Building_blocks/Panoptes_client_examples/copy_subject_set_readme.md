## Copy Subject Set

This script is written in Python3.62 and requires the panoptes_client to be installed.

To use the script your zooniverse user-name and password must be set in your Operating System as Environment Variables for the keys User_name and Password. Alternately you can hardcode your username and password in the code as shown below but then you must secure the code to protect your password..

````Panoptes.connect(username='user_name', password='password')````

If you attempt to connect to a project for which you are not authorized as a owner or collaborator the script will respond 

````subject set not found or not accessible````

Unfortunately the error handling is very crude and does not tell you exactly what went wrong.

The script first asks you for the source project id and the subject_set name, and attempts to access this subject set.  If the set is not found or is not accessible to you have the option to try again or exit. It is best to copy and paste the subject set name directly from the project builder since it is both case sensitive and spaces and punctuation count.

The script then queries the subject set and creates a list of subjects in it that need to be copied to the destination.  This can take some time - many minutes for large sets.

The script then asks for the project id and subject set name for the destination subject set.  Again an attempt to access a project you do not have access to will produce the output

````Project not found or accessible````

with the opportunity to try again or exit.

The script then locates the destination subject set or proceeds to create it and link it to the specified project.  The script then proceeds to link the subjects in the list from above one at a time verifying they linked to the new subject set for each subject. Subjects in the destination subject set previously linked or those that did not link due to communication errors or other causes will report 

````previously linked or did not link correctly````

The total number of subjects linked is reported.  If some subjects were already linked to the destination subject set this number will not be the same as the length of the list of source subjects.

The script then queries the new subject set directly and produces a list of the subjects linked to it.  That list should be the same length as the source subject set. The list is saved to a file  'copied_subjects.csv'.  Again this takes a few minutes. 
