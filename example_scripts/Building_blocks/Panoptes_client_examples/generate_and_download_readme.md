## Generate Classification and Subject exports

The script generate_export.py logs into the Panoptes client using User_name and Password previously set up as Environmental Variables in your Operating system.  Alternately these can be hardcoded if the code is kept secure to protect your password. It is also necessary to hardcode the desired project slug in line 7 to use the script as a stand-alone rather than a module.

The script first tests to see if 24 hours have elapsed since the last classification export was requested, and warns and terminates if not. If the last export request is more than 24 hours previous it attempts to generate a new one.  The script then waits 30 seconds for Panoptes to begin to create the export and then tests to see if that has happened. If not it warns the export request is not being produced.

These same steps are then repeated for the Subject export.

## Download exports and slice

The script download_export_and_slice.py logs into the Panoptes client using User_name and Password previously set up as Environmental Variables in your Operating system.  Alternately these can be hardcoded if the code is kept secure to protect your password. It is also necessary to hardcode the desired project slug in line 7 to use the script as a stand-alone rather than a module.
The destination path and filenames for both the classification file and the subject export need to be hardcoded, as well as the locations for the sliced output to use the script as a stand_alone, or explicitly passed to the functions if called as modules. 


Unlike the code suggested in the Panoptes Client documentation, this script can handle large export files (easily > 1Gb) since it does not read the file into memory all in one go but streams the data to a file in chunks. All subsequent operations from the file after they are opened for slicing are handled by Python to avoid overloading the memory available.

The download and slicing can take several minutes for larger files (about 3 minutes per Gb for my hardware, internet connection and when zooniverse is not too busy - all three things will affect the time.)

The script determines the age of the classification export file based on the current time and the last update to the export.  This age is calculated for EST - other time zones will need to change the hardcoded offset to zulu time.  If the export file has not completed generating, the download will fail with the message 'Classifications download did not complete' and the function returns False.

If the generated export file exists it is then downloaded to the file specified as the destination.  This operation is handled by the Python package requests using request.iter_content and has been quite robust. You may be able to optimize it slightly for your situation by changing the chunk size though 4096 works well for me.  Once the file is complete a message to that effect is printed, and the function returns True. If the download fails for any reason the error is handled, a warning message is printed and the function returns False

The script then does the same for the subject export.  If other exports are required, minor modifications of this function can handle the other exports as well.

The next function slice_exports uses an only slightly modified flatten_class_frame.py to set up logical tests for records to be included in the slice. See the documentation for that script for details.  The specific limits and conditions need to be hardcoded based on your project workflows, subject sets and subject id ranges.  (Note classification export files have a field subject_ids with an s while the subject export has subject_id with no s)

Using the appropriate conditions and limits any part of either of the exports can be extracted into much smaller files for further processing.  Since it is likely that the reduced classification file will be processed multiple times for various purposes it makes sense to do the slice once per download rather than leave it to the flattening step, though further slicing can be done there as well.

The script supplies a short report of records read and processed (sliced) into the shortened files.  If the functions complete with no errors they return True.
