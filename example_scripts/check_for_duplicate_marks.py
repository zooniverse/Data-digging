"""
Zooniverse.org - Check For Duplicate Marks v3.0
-----------------------------------------------

Checks for duplicate 'point-type drawing task' annotation marks in Zooniverse
Classifications. A mark is considered a duplicate if it has the same {x, y}
value as a previous annotation mark.

Context:
https://github.com/zooniverse/Panoptes-Front-End/issues/5527

Requires:
- A Classifications export from Zooniverse.org to analyse. Only applicable for
  Project Workflows that use the point-type too for drawing tasks.

Usage:
python (thisfile).py (zooniverse_classifications_export).csv

Output:
prints out a list (in CSV format) of every Classification with any duplicate
marks, the web browser the user was using (useful for determining if, e.g. most
of the duplicates come from certain touchscreen devices), and the number of
duplicate marks detected.

Notes:
- the output file doesn't detail WHICH marks in an annotation are duplicates,
  but this script can be modified to output that, if you're curious.
  Look for the block of code marked as LIST_ALL_DUPLICATES below.

Pro Tips:
- You can write the the list to a file:
  python (thisfile).py (zooniverse_classifications_export).csv > duplicates.csv
- You can compare the number of Classifications with duplicates vs the number of
  total Classifications: (remember to minus 1 from the numbers to account for
  the header row)
  wc -l duplicates.csv zooniverse_classifications_export.csv
  
History:
- Original code published 2019.10.29 
- Updated on 2020.04.22 to correct for actual format of Classifications exports
  from Zooniverse.org. Delimiter was changed from ';' to ',' and the 'id' column
  renamed to 'classification_id'.

(@shaunanoordin 2020.04.22)

"""

import sys, csv, json

#-------------------------------------------------------------------------------

if len(sys.argv) < 2:
  print('Zooniverse.org - Check For Duplicate Marks')
  print('--------')
  print('Usage: python (thisfile).py (zooniverse_classifications_export).csv ')
  sys.exit(0)

input_filename = sys.argv[1]

#-------------------------------------------------------------------------------

def main(input_filename):
  try:
    with open(input_filename) as input_file:
      reader = csv.DictReader(input_file, delimiter=',', quotechar='"')

      total_rows = 0
      rows_with_duplicates = 0
      
      try:
        
        print_classification_header()
        for row in reader:
          annotations = get_json_object(row['annotations'])
          duplicates = find_duplicates_in_annotations(annotations)
          
          if len(duplicates) > 0:
            rows_with_duplicates += 1
            print_classification(row, duplicates)
          total_rows += 1

      except csv.Error as err:
        print('[CSV ERROR]')
        print(err)
        raise err

  except Exception as err:
    print('[GENERAL ERROR]')
    print(err)
    sys.exit('GENERAL ERROR')

#-------------------------------------------------------------------------------

def print_classification_header():
  print(
    '"classification_id",' +
    '"user_id",' +
    '"created_at",' +
    '"session",' +
    '"user_agent",' +
    '"num_of_duplicates"'
  )

def print_classification(classification, duplicates):
  try:
    metadata = get_json_object(classification['metadata'])
    print(
      '"' + classification['classification_id'] + '",' +
      '"' + classification['user_id'] + '",' +
      '"' + classification['created_at'] + '",' +
      '"' + metadata['session'] + '",' +
      '"' + metadata['user_agent'] + '",' +
      '"' + str(len(duplicates)) + '"'
    )
  except Exception as err:
    print('[ERROR] could not print classification: ', err)
    
#-------------------------------------------------------------------------------
    
def get_json_object(json_string):
  try:
    return json.loads(json_string)
  except:
    return {}

#-------------------------------------------------------------------------------

def find_duplicates_in_annotations(annotations):
  '''
  Finds all "point drawing task" annotations that have duplicates. An annotation
  value is a "duplicate" if it shares the same x and y as a previous annotation
  value.
  
  Returns an array: [{ x, y, count }]
  
  All incompatible tasks (e.g. "multiple-choice answer" tasks, which have values
  of "1" or "5" instead of [{x, y, ...}], are ignored. Or rather, they're
  dumped straight into the Exception handler.
  '''
  
  try:
    duplicates = []

    for task in annotations:
      
      # Go through every annotation and store the count of each unique value
      known_values = []
      
      for val in task['value']:
        found = False
        
        for kval in known_values:
          if kval['x'] == val['x'] and kval['y'] == val['y']:
            kval['count'] += 1
            found = True
        
        if not(found):
          known_values.append({
            'task': task['task'],
            'x': val['x'],
            'y': val['y'],
            'count': 1
          })
      
      # Check if there are any unique annotation values that appeared more than once
      for kval in known_values:
        if kval['count'] > 1:
          duplicates.append(kval)
    
    # LIST_ALL_DUPLICATES
    # Un-comment the following block if you want to see all the duplicate marks
    # listed in detail.
    # WARNING: this will invalidate the CSV format of the output.
    # --------
    # if len(duplicates) > 0:
    #   print('--------')
    #   for evil_twin in duplicates:
    #     print(evil_twin)
    # --------
    
    return duplicates

  except Exception as err:
    return []
  
#-------------------------------------------------------------------------------

main(input_filename)