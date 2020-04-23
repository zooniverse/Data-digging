## Working with Notes From Nature’s Reconcile Transcripts

I had considerable difficult getting this python script to run in Windows, entirely due to obtaining and installing the required packages in a Windows environment – once the required packages were installed and one small issue was resolved the software ran flawlessly.
So this is what I did in Windows 7 Professional to get this up and running:

## 1) Installation -

The original instructions at the time were:

•	We require python 3.4 or later

•	git clone https://github.com/juliema/label_reconciliations

•	cd label_reconciliations

•	It is recommended that you use a Python virtual environment for this project.

•	Optional: virtualenv venv -p python3

•	Optional: source venv/bin/activate

•	pip install -r requirements.txt


**What I actually did:** (I am running Python 3.6.2, and do not have Git Desktop)

To obtain a copy of the code - from “Clone or download” I chose “Download zip” and saved it to a file. 

I then opened the file in Downloads in Windows Explorer and used “extract all” to a known directory.

I then created a sub-director in my normal Python directory C:\py\label_reconciliations and copied the extracted files to it. (keeping the originals just in case things went wrong)

After attempting to follow the balance of the instructions I realized Windows was not getting through the pip install and that Scipy in particular had no directly usable binaries for Windows.
I decided to modify my current Python set up (which already had some of the required dependencies installed (notably Numpy and some others)) rather than set up a virtual environment. 

There are reasons one might want to set up a virtual environment (for example in case a future change to Python or some package is not backwards compatible with this code).  However the current added complexity was assumed to be more trouble than potential future problems.

Looking through the requirements.txt file I could see we needed Numpy, pandas, Scipy, ipython, and others.  Some of them I knew I already had, while others I knew I needed.   I already knew Scipy was a problem for Windows so I visited the go-to website for Windows solutions to python package issues:  http://www.lfd.uci.edu/~gohlke/pythonlibs/ where Christoph Gohlke has already solved these problems and we need only know which of the several wheel versions we need for our Windows version.

To get the Windows version information you need to pick the right wheel, go to Control Panel –System this will tell you if your system is 32 or 64 bit and your processor type.  Chose the correct wheel based on your Python version and Windows version – in my case those that end with cp36m win32.whl.

To install wheels, download them to a file in Downloads then run

pip install C:\path\downloaded.whl

by typing that in the Start “Search programs and files” box and executing the command that is “found”.

I had already installed numpy but you may need to, from Christoph Gohlke:

pip install C:\path\numpy 1.13.1+mkl cp36 cp36m win32.whl 

I then installed pandas with a clean pip install (pandas is supported for Windows directly)

pip install pandas

and then I installed Scipy, again from Christoph Gohlke

pip install C:\path\scipy 0.19.1 cp36 cp36m win32.whl

At that point I started to attempt to run reconcile.py.  There was a bit of a learning curve to get the right parameters after the file name to get it to run (See below) but what is important here is some other additional dependencies were quickly identified and in short order I loaded
 
pip install inflect

pip install fuzzywuzzy

pip install ipython

I already had ‘urllib3’ and ‘requests’ - you may need those as well… the point is once you start running the code the error messages will tell you what you need to install – this method is messy and a little slow but it has the advantage that you can install each package separately and know you have it whereas a failure of pip install –r requirements.txt does not tell you what went wrong, it just doesn’t work.

Finally I got the code running with only a warning concerning not having Python-Levenshtein, so I got that from Christoph Gohlke as well:

pip install C:\path\python_Levenshtein 0.12.0 cp36 cp36m win32.whl

At this point the code is working with no error messages, though there is the possibility that additional packages may be needed as I use sections of the code I have not yet explored.  In that case I will obtain and install them as needed.

## 2)  Running the NfN reconcile.py on Zooniverse NFN classification downloads

To ensure we can correctly run reconcile.py it is best to get everything working with the certified nfn data in the repository.

To run reconcile.py one has to include a list of arguments or parameters after the file name. These are defined in reconcile,py.  To get the list of options and their meaning the original documentations states:

‘You may get program help via:  
`python reconcile.py –h`’

Which gives the following output:
````
usage: reconcile.py [-h] [-f {nfn,csv,json}] [-c COLUMN_TYPES]
                    [-u UNRECONCILED] [-r RECONCILED] [-s SUMMARY] [-m MERGED]
                    [-z ZIP] [-w WORKFLOW_ID] [--title TITLE]
                    [--group-by GROUP_BY] [--key-column KEY_COLUMN]
                    [--user-column USER_COLUMN] [--page-size PAGE_SIZE]
                    [--fuzzy-ratio-threshold FUZZY_RATIO_THRESHOLD]
                    [--fuzzy-set-threshold FUZZY_SET_THRESHOLD] [-V]
                    INPUT-FILE

This takes raw Notes from Nature classifications and creates a
reconciliation of the classifications for a particular workflow.
That is, it reduces n classifications per subject to the "best"
values. The summary file will provide explanations of how the
reconciliations were done. NOTE: You may use a file to hold the
command-line arguments like: @/path/to/args.txt.

positional arguments:
  INPUT-FILE            The input file.

optional arguments:
  -h, --help            show this help message and exit
  -f {nfn,csv,json}, --format {nfn,csv,json}
                        The unreconciled data is in what type of file? nfn=A
                        Zooniverse classification data dump. csv=A flat CSV
                        file. json=A JSON file. The default is "nfn". When the
                        format is "csv" or "json" we require the --column-
                        types. If the type is "nfn" we can guess the --column-
                        types but the --column-types option will still
                        override our guesses.
  -c COLUMN_TYPES, --column-types COLUMN_TYPES
                        A string with information on how to reconcile each
                        column in the input file. The format is --column-types
                        "foo x:select,bar:text,baz:text". The list is comma
                        separated with the column label going before the colon
                        and the reconciliation type after the colon. Note:
                        This overrides any column type guesses. You may use
                        this multiple times.
  -u UNRECONCILED, --unreconciled UNRECONCILED
                        Write the unreconciled workflow classifications to
                        this CSV file.
  -r RECONCILED, --reconciled RECONCILED
                        Write the reconciled classifications to this CSV file.
  -s SUMMARY, --summary SUMMARY
                        Write a summary of the reconciliation to this HTML
                        file.
  -m MERGED, --merged MERGED
                        Write the merged reconciled data, explanations, and
                        unreconciled data to this CSV file.
  -z ZIP, --zip ZIP     Zip files and put them into this archive. Remove the
                        uncompressed files afterwards.
  -w WORKFLOW_ID, --workflow-id WORKFLOW_ID
                        The workflow to extract. Required if there is more
                        than one workflow in the classifications file. This is
                        only used for nfn formats.
  --title TITLE         The title to put on the summary report. We will build
                        this when the format is nfn. For other formats the
                        default is the INPUT-FILE.
  --group-by GROUP_BY   Group the rows by this column (Default=subject_id).
  --key-column KEY_COLUMN
                        The column containing the primary key
                        (Default=classification_id).
  --user-column USER_COLUMN
                        Which column to use to get a count of user
                        transcripts. For --format=nfn the default=user_name
                        for other formats there is no default. This will
                        affect which sections appear on the summary report.
  --page-size PAGE_SIZE
                        Page size for the summary report's detail section
                        (Default=20).
  --fuzzy-ratio-threshold FUZZY_RATIO_THRESHOLD
                        Sets the cutoff for fuzzy ratio matching (0-100,
                        default=90). See
                        https://github.com/seatgeek/fuzzywuzzy.
  --fuzzy-set-threshold FUZZY_SET_THRESHOLD
                        Sets the cutoff for fuzzy set matching (0-100,
                        default=50). See
                        https://github.com/seatgeek/fuzzywuzzy.
  -V, --version         show program's version number and exit

Current reconciliation types
----------------------------
  select: Reconcile a fixed list of options.
  text:   Reconcile free text entries.
  same:   Check that all items in a group are the same.
  mmm:    Show the mean, median, and mode for each group.
* Note:   If a column is not listed it will not be reconciled.
````


To use this code on a nfn zooniverse classification download we simply need to define the output files and input files with the simplest command line:

reconcile.py -r data\reconciled.csv -s data\summary.html data\classifications-from-nfn.csv

While we could use this with the data file included in the repository, it is some 95Mb and contains many different workflow_ids  This requires adding –w XXXX after the summary argument.  XXXX is an integer which is the number of the workflow you want reconciled. The command line for workflow 1930 becomes:

reconcile.py -r data\reconciled.csv -s data\summary.html –w 1930 data\classifications-from-nfn.csv


## 3) Running the NfN reconcile.py on Flattened csv files

To use this code specifically on non-nfn files they need to be flattened csv files with one text string per field that we want reconciled between entries.  Several of the parameters will be needed to be set explicitly:

-f  is the csv option.

-c  define the columns we want reconciled in format field_name:text where field name(s) are the field names in the flattened csv file. Only the specified columns will be reconciled.

-r  path and the name of the reconciled output file.

-s  (optional) path and the name of the summary html file.

--user-column  is the field name for the classifiers names: user_name

Location and name of input flattened csv file.


This will look like this:

reconcile.py -f csv  -c “field_name_1:text,field_name_2:text,…field_name_N:text” -r path\reconciled_file_name.csv  -s path\summary_file_name.html  --user-column user_name  path\input_file_name.csv

In theory one can store this in a file but I was unable to make that work so I stored what did work in a notepad txt file and copied just text across to the “Script parameters” line under “Add parameters” in the editor (right click on green run arrow).

One small point - the zooniverse classification file holds the subject_ids in a column with header 'subject_ids' (with an 's'). For nfn formatted files the 's' is required, but for **csv formatted files** the subject_ids must be in a column headed **'subject_id' ( no 's')**

See the flatten_class_transcription_demo.py (and assocoated files) for an example of a non-nfn zooniverse classification file flattened suitably for this reconciliation process.
