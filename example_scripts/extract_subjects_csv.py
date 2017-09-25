import sys
import numpy as np
import pandas as pd
import json


"""
function flattenDict from https://gist.github.com/higarmi/6708779

example: The following JSON document:
{"maps":[{"id1":"blabla","iscategorical1":"0", "perro":[{"dog1": "1", "dog2": "2"}]},{"id2":"blabla","iscategorical2":"0"}],
"masks":{"id":"valore"},
"om_points":"value",
"parameters":{"id":"valore"}}

will have the following output:
{'masks.id': 'valore', 'maps.iscategorical2': '0', 'om_points': 'value', 'maps.iscategorical1': '0',
'maps.id1': 'blabla', 'parameters.id': 'valore', 'maps.perro.dog2': '2', 'maps.perro.dog1': '1', 'maps.id2': 'blabla'}
"""

def flattenDict(d, result=None):
    if result is None:
        result = {}
    for key in d:
        value = d[key]
        if isinstance(value, dict):
            value1 = {}
            for keyIn in value:
                value1[".".join([key,keyIn])]=value[keyIn]
            flattenDict(value1, result)
        elif isinstance(value, (list, tuple)):
            for indexB, element in enumerate(value):
                if isinstance(element, dict):
                    value1 = {}
                    index = 0
                    for keyIn in element:
                        newkey = ".".join([key,keyIn])
                        value1[".".join([key,keyIn])]=value[indexB][keyIn]
                        index += 1
                    for keyA in value1:
                        flattenDict(value1, result)
        else:
            result[key]=value
    return result

# define path and read export file
path = './'
infile = path+'subject_export.csv'
subj = pd.read_csv(infile)

# if you're pasting this at the ipython prompt, type subj.head(5) to get a sense of the table from the first 5 rows

# different subject sets can have wildly different metadata
# actually there can be really different data within a subject set, but I'm assuming most of the difference will be between subject sets
# so get the subject sets and make different files for each to minimize ridiculous empty columns
subject_sets = subj.subject_set_id.unique()

# interpret the metadata string as a json
subj['metadata_arr'] = subj.metadata.apply(json.loads)
# then flatten it (csv doesn't like nesting)
subj['metadata_flat'] = subj.metadata_arr.apply(flattenDict)
# this is probably unnecessary but just in case we want to keep a copy of the original flattened one
subj['metadata_all'] = subj.metadata_flat.copy()

# add the subject id to the dict so we can deal with this as 1 thing later
for idx, row in enumerate(subj.iterrows()):
	# row[0] should be the index of the row, for future reference
    row[1]['metadata_all']['subject_id'] = row[1]['subject_id']
    row[1]['metadata_all']['locations'] = row[1]['locations']

# save the keys in a new column
subj['metadata_keys'] = [q.keys() for q in subj.metadata_all]

# get unique set of keys
# this is for if you want all subjects in the same (possibly huge) file, ie if you're not using the loop below
#keyset = set(subj.metadata_keys.sum())

# write different files for different subject sets
for sset in subject_sets:
    outfile = path + 'subject_set_%d_export.csv' % sset
    thisset = subj[subj.subject_set_id == sset]
    # get unique set of keys to cover all data in all rows in the file
    # this line takes a little while
    keyset = set(thisset.metadata_keys.sum())

    # now write to this subject set's file
    f = open(outfile,'wb')
    w = csv.DictWriter(f, keyset)
    w.writeheader()
    w.writerows(thisset.metadata_all)
    f.close()
