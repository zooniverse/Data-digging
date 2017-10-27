'''This code is not functional as it is presented.  Parts of it must be placed into the flatten_classification_frame.py
in the appropriate way following the step by step instructions in the comments and the example of
flatten_classification_general_utilities-demo.py.  Only the blocks required need be used, and some of them
(Block 1,2 and 3) perform the same basic function in different ways.   See the flatten_classification_frame_readme.md
for further information on what each block does'''

#______________________________________________________________________________________________________________________

# Block 1 generates a user_name for not_signed_in users based on an external cross reference
    # First add the file location for the cross-reference to the list of locations near the top
name_location = r'modify this text to full path and file name including extension (.csv) for assigned name file'
    # Second, copy the function definition to flatten_classification_frame.py and place it
    # with the other functions near the top.
def load_pick_ip():
    with open(name_location) as name:
        ipdict = csv.DictReader(name)
        assigned_name = {}
        for ipline in ipdict:
            # NOTE! This code assumes the external picklist is a csv file with two fields 'user_ip' and
            # 'assigned_name'. If the field names are different the following line must be modified to match them:
            assigned_name[str(ipline['user_ip'])] = ipline['assigned_name']
        return assigned_name
    # Third, place this statement in the block which initializes i and j prior to entering the loop
    # to iterate over the classification records
    name_list = load_pick_ip()
    # Fourth, add the code below to the middle section of the Frame where the functional code blocks can operate
    #  on each record in turn
                # generate user_name for not_signed_in users
                user_name = str(row['user_name'])
                if row['user_id'] == '':
                    try:
                        user_name = name_list[str(row['user_ip'])]
                    except KeyError:
                        #  Various options for the case no user_name was assigned to that user_ip  - pick one!
                        user_name = 'Visitor'  # this lumps them all together
                        user_name = str(row[user_name])  # leaves the default "not-logged-in plus user_ip"
                        user_name = row['user_ip']  # uses user_ip as user_name
    # Lastly, replace 'row['user_name'] with user_name as the value for 'user_name' in the writer ie
                        'user_name': user_name,
#______________________________________________________________________________________________________________________


# The following section has three code blocks that seek to determine an image_number
# which is of significance to the project, either by using an external cross reference
# or parsing it out of the subject_data that was uploaded with the subject images(metadata)

# Block 2: Use a subject_ids-image_name cross-reference to add image_numbers
    # First add the file location for the cross-reference to the list of locations near the top
image_location = r'modify this text to full path and file name including extension (.csv) for image_number file'
    # Second, copy the function definition to flatten_classification_frame.py and place it
    # with the other functions near the top.
def load_pick_image():
    with open(image_location) as image:
        subject_dict = csv.DictReader(image)
        assigned_number = {}
        for subject_line in subject_dict:
            # NOTE! This code assumes the external picklist is a csv file with two fields 'subject_ids' and 
            # 'image_number'. If the field are different the following line must be modified to match them:
            assigned_number[str(subject_line['subject_ids'])] = subject_line['image_number']
        return assigned_number
    # Third, place these two statements in the block which initializes i and j prior to entering the loop
    # to iterate over the classification records
    image_list = load_pick_image()
    no_image = []
    # Fourth, add the code below to the middle section of the Frame where the functional code blocks can operate
    #  on each record in turn
                #  Pull image_numbers from the external cross reference load above
                try:
                    image_number = image_list[str(row['subject_ids'])]
                except KeyError:
                    image_number = 'No_image'
                    no_image.append(row['subject_ids'])
    # Fifth, add an image_number field to the list of file names and to the writer with value image_number
    # Lastly, add a status print to the end of the frame code
         print('subjects with no image number', no_image)
#_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _

# Block 3: Use string functions to pick out file names that are in the subject_data field of each classification
# this approach only works if every subject had the appropriate metadata uploaded with it in a consistent format.
# if this is not the case prepare an external cross reference and use Block 2.
    # This code is placed in the middle section of the Frame where the functional code blocks go.  The only
    # other step is to add an image_number field to the list of file names and to the writer with value image_number
                #generate image_number from the subject data field Example 1
                #  Subject_data contains text similar to this:
                # '{"3350842":{"retired":null,"Filename":"RUTA470M_Sector4_190816094.jpg"}}'
                line = str(row['subject_data'])
                start = line.find('Filename')
                end = line.find('.jpg')
                # having found the start and end of the filename text, adjust the offsets to slice the string
                # exactly where you want (note start = the first character  of the search string, and end does
                # not include the search string.
                image_number = line[start + 12:end]
#_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _


# Block 4: Uses string functions to pick out camera image numbers that are in the subject_data field of each
# classification. This approach only works if every subject had the appropriate metadata uploaded with it in
# a consistent format. If this is not the case prepare an external cross reference and use Block 2.
    # This code is placed in the middle section of the Frame where the functional code blocks go.  The only
    # other step is to add an image_number field to the list of file names and to the writer with value image_number
                # generate image_number from the subject data field Example 2
                #  Subject_data contains text similar to this:
                # 'Image_Name":"DSC089442015_02_12_10.jpg'
                line = str(row['subject_data'])
                # find a distinct start and end for the desired text
                start = line.find('DSC')
                end = line.find('.jpg')
                # apply suiable offsets to get the exact parts you want
                date = line[start + 8:end - 3]
                number = line[start + 3:start + 8]
                # rearrange and format so field will be a sortable string (ie avoid dates and number formats
                #  unless there is a need for the complexity)
                image_number = 'F' + date.replace('_', '') + number + line[end - 2:end]
#______________________________________________________________________________________________________________________


# Block 5  Uses the 'started at' and 'finished at' times of the metadata to calculate the time taken to do
# each classification. If the time is greater than 24 hours it defaults to 24 hours.
    # This code is placed in the middle section of the Frame where the functional code blocks go.  The only
    # other step is to add an elapsed_time field to the list of file names and to the writer with value tdelta
                # generate the classification elapsed_time, which is more useful than start/finish times
                #  "started_at":"2015-08-21T07:34:22.193Z",....,"finished_at":"2015-08-21T07:34:31.928Z"...
                line = str(row['metadata'])
                start = line.find("started")
                end = line.find('Z', start)
                begin = line[start + 13:end - 4]
                start = line.find('finished')
                end = line.find('Z', start)
                finish = line[start + 14:end - 4]
                tdelta = datetime.strptime(finish, '%Y-%m-%dT%H:%M:%S') - datetime.strptime(begin, '%Y-%m-%dT%H:%M:%S')
                if len(str(tdelta)) > 8:
                    tdelta = '24:00:00'
#______________________________________________________________________________________________________________________


# Block 6 This block uses the image dimensions from the metadata field to produce an image_size tuple
    # First, place this statement in the block which initializes i and j prior to entering the loop
    # to iterate over the classification records
    no_size = []
    # Second, add the code below to the middle section of the Frame where the functional code blocks can operate
    # on each record in turn. Set the defaults for cases the dimensions in the metadata are not found.  The code
    #  also produces a list of classifications where the dimensions are missing which can be manually repaired if
    #  the defaults are not correct or missing (the dimensions are missing in about 1 in 10,000 records).
                # generate scale from metadata
                dimensions = metadata['subject_dimensions']
                widths = dimensions[0]
                if widths is not None:
                    image_size = json.dumps([round(widths['naturalWidth']),
                                             round(widths['naturalHeight'])])
                else:
                    no_size.append(row['classification_id'])
                    image_size = json.dumps([some default, values here])
    # Fourth, add an image_size field to the list of file names and to the writer with value image_size
    # Lastly, add a status print to the end of the frame code
            print('classifications with no image size', no_size)
#______________________________________________________________________________________________________________________
