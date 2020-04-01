This script is a demo for the flatten_class_frame where it is used to slice out (or select) two specific subject numbers for the Aerobotany classification download.

This script demonstrates shows the basic script flatten_class_frame.py modified in four ways:
 1) The actual path and file names were modified to match the files on my drive. You would have to modify these to match your file locations, and chose your own name for the output file based on what you are doing.
 2) The comment lines have been stripped out - This script is actually fairly short! This is not necessary but shows how the script can be simplified.  
 3) Unused slice conditions have been deleted except for one we want which selects only two subject_ids.  Alternately the unused code could be left in place and “#” characters placed before each line (this is known as “commenting out” sections of code).
 4) The output file field names and the writer line have been simplified by eliminating many of the fields that were not required to give us the info we wanted which was to determine if the retirement limit was met for these two subject numbers for a specific workflow (The output file showed that they were. - gold standard classifications done under a different workflow did NOT reduce the regular classification limit).

Keep in mind this script is meant to be a frame work to contain many other blocks of code that will perform many other functions than slicing out specific records and fields.  This first demo only covers the basic slicing function.

This is the modified code:

    import csv
    import json
    import sys
    from datetime import datetime

    csv.field_size_limit(sys.maxsize)

    location = r'C:\py\AAClass\amazon-aerobotany-classifications_2017-03-18.csv'
    out_location = r'C:\py\AAClass\flatten_class_demo_output.csv'


    # define a function that returns True or False based on whether the argument record is to be included or not in
    # the output file based on the conditional clauses.

    def include(class_record):
        if int(class_record['subject_ids']) == 4985936 or int(class_record['subject_ids']) == 4989858:
            pass
        else:
            return False
        return True


    with open(out_location, 'w', newline='') as file:
        fieldnames = ['classification_id',
                      'user_ip',
                      'workflow_id',
                      'workflow_version',
                      'created_at',
                      'gold_standard',                  
                      'subject_ids']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()

        i = 0
        j = 0
        with open(location) as f:
            r = csv.DictReader(f)
            for row in r:
                i += 1
                if include(row) is True:
                    j += 1

                    writer.writerow({'classification_id': row['classification_id'],
                                     'user_ip': row['user_ip'],
                                     'workflow_id': row['workflow_id'],
                                     'workflow_version': row['workflow_version'],
                                     'created_at': row['created_at'],
                                     'gold_standard': row['gold_standard'],                                 
                                     'subject_ids': row['subject_ids']})

                    print(j)
            print(i, 'lines read and inspected', j, 'records processed and copied')
            #

And the output:

classification_id | user_ip              | workflow_id | workflow_version | created_at              | gold_standard | subject_ids 
-------------------|----------------------|-------------|------------------|-------------------------|---------------|-------------
 23141171          | 93d99f07ead1f27bc80a | 2575        | 38.117           | 2016-12-11 23:50:43 UTC | TRUE          | 4985936     
 23141210          | 93d99f07ead1f27bc80a | 2575        | 38.117           | 2016-12-11 23:54:10 UTC | TRUE          | 4989858     
 23167355          | 7776e6bfd4cb78197529 | 3130        | 1.13             | 2016-12-12 15:57:26 UTC |               | 4989858     
 23167576          | 43b87cf99da874ac45ed | 3130        | 1.13             | 2016-12-12 16:00:37 UTC |               | 4985936 
 23191925          | 82889433b8968b9c8993 | 3130        | 1.13             | 2016-12-12 21:44:24 UTC |               | 4989858     
 23192574          | 443c099c5aa147e3da7f | 3130        | 1.13             | 2016-12-12 21:55:49 UTC |               | 4989858     
 23210538          | e0b070c40944289bce09 | 3130        | 1.13             | 2016-12-13 06:24:42 UTC |               | 4989858     
 23314374          | 560a5276186608c68089 | 3130        | 1.13             | 2016-12-14 23:16:15 UTC |               | 4985936     
 23423350          | 90dd7586160e693dc2c9 | 3130        | 1.13             | 2016-12-16 22:20:46 UTC |               | 4985936     
 23451676          | 7b944fb27ff094ca74c8 | 3130        | 1.13             | 2016-12-17 16:14:23 UTC |               | 4989858     
 23474212          | 0e5195b48dcfeda1193a | 3130        | 1.13             | 2016-12-18 03:05:49 UTC |               | 4985936     
 23495511          | 992c27878f2c37a6c038 | 3130        | 1.13             | 2016-12-18 18:42:18 UTC |               | 4989858     
 23654054          | 294fe10cd3c5a4466822 | 3130        | 1.13             | 2016-12-21 18:59:37 UTC |               | 4985936     
 23864011          | 8b9a87f643fd8d7afb7e | 3130        | 1.13             | 2016-12-27 19:53:32 UTC |               | 4985936     
 24020764          | 662c0a6e638c503fe8be | 3130        | 1.13             | 2016-12-31 20:28:57 UTC |               | 4985936     
 24042667          | 628fb8940e73d4f2bdf9 | 3130        | 1.13             | 2017-01-01 15:14:39 UTC |               | 4985936     
 24080224          | 7b944fb27ff094ca74c8 | 3130        | 1.13             | 2017-01-02 17:33:18 UTC |               | 4985936     
 24160202          | 9852f1d410bff86a271c | 3130        | 1.13             | 2017-01-04 17:33:02 UTC |               | 4985936     
 24194672          | a49c950ccca551cdd90d | 3130        | 1.13             | 2017-01-05 14:38:56 UTC |               | 4989858     
 24274708          | 2262a04a9152aa28c580 | 3130        | 1.13             | 2017-01-06 22:06:37 UTC |               | 4989858     
 24295544          | a49c950ccca551cdd90d | 3130        | 1.13             | 2017-01-07 11:35:52 UTC |               | 4985936     
 24510123          | c1408594c75a632040f1 | 3130        | 1.13             | 2017-01-11 18:06:22 UTC |               | 4985936     
 24712891          | 992c27878f2c37a6c038 | 3130        | 1.13             | 2017-01-14 05:10:22 UTC |               | 4985936     
 25694763          | 3326bfbdc64319196c47 | 3130        | 1.13             | 2017-01-25 02:05:41 UTC |               | 4989858     
 25761044          | 55f0ab21d652c28d6a4c | 3130        | 1.13             | 2017-01-25 22:38:41 UTC |               | 4985936     
 26485985          | 93606fa91a533f245768 | 3130        | 1.13             | 2017-02-03 01:13:49 UTC |               | 4985936     
 26649867          | b67c225e70378e9e8ea5 | 3130        | 1.13             | 2017-02-05 23:53:31 UTC |               | 4989858     
 26682226          | 5bd1ca30d4a67bc19d91 | 3130        | 1.13             | 2017-02-06 17:10:19 UTC |               | 4989858     
 27493912          | 01d344a4cfc6210a35ad | 3130        | 1.13             | 2017-02-16 19:09:04 UTC |               | 4989858     
 28200170          | 4513ae94b88bd115b9a2 | 3130        | 1.13             | 2017-02-18 21:25:52 UTC |               | 4989858     
 28831200          | 40ee67c352f329c2c1b9 | 3130        | 1.13             | 2017-02-20 18:02:40 UTC |               | 4989858     
 29099281          | 5ec3fe0df7211efcd86b | 3130        | 1.13             | 2017-02-21 16:21:02 UTC |               | 4989858 
 

