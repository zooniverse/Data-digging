import argparse
import json
import os
import sys

import numpy as np
import pandas as pd

try:
    from panoptes_client import Panoptes, SubjectSet
except ImportError:
    print('Install https://github.com/zooniverse/panoptes-python-client')
    sys.exit(1)


def JSONParser(data):
    """call json.loads"""
    return json.loads(data)


def load_classifications(filename, json_columns=None):
    """
    Load classifications into pandas dataframe.

    Some columns of the csv are embedded json and need special parsing.
    """
    json_columns = json_columns or ['metadata', 'annotations', 'subject_data']
    converters = {i: JSONParser for i in json_columns}

    return pd.read_csv(filename, converters=converters)


def unpack(series):
    """
    Return the first value in a series.

    All annotations values are lists because of a few multiple tasks.
    The second multiple task always has the value of 'None of the above'
    (For this dataset!)
    """
    return [a[0] for a in series]


def parse_classifications(filename):
    """
    Load classifications and datamunge annotations column.
    """
    data = load_classifications(filename)

    # Only need the first item in the annotations list of json objects
    data['annotations'] = unpack(data['annotations'])
    return data


def explore(data):
    """
    print the values are in the annotations
    """
    import numpy as np
    values = np.unique(np.concatenate([a['value']
                                       for a in data['annotations']]))
    print(values)
    return


def cull_subject_ids(filename, w2s=None, overwrite=False, add=False):
    """
    Cull classifications file and write to new workflows.

    Parameters
    ----------
    filename : str
        input csv file

    ws2 : dict
        key: workflow title (for file naming)
        value: Single string to select on within annotations values.

    overwrite : bool [False]
        overwrite with new file
    """
    # load and munge data
    data = parse_classifications(filename)

    if w2s is None:
        # see, e.g., explore(data)
        w2s = {'2a': 'A single sky\xa0figure *with* axes labeled',
               '2b': 'Two or more sky figures *with* axes labeled',
               '2c': 'Sky figure(s) *without* axes labeled'}
        # Empty set IDs created on the web interface
        subject_set_ids = {'2a': 12651,
                           '2b': 8433,
                           '2c': 12645}

    for wf in w2s.keys():
        # new filename assumes wf1 is in the first filename!
        outname = filename.replace('classifications_wf1',
                                   'subject_ids_wf{0:s}'.format(wf))

        # Identifiy matches to next workflow
        iwf = [w2s[wf] in a['value'] for a in data['annotations']]

        # create sub-copy of dataframe with only workflow matches
        df = data['subject_ids'].iloc[iwf]

        # write ... or not
        if not os.path.isfile(outname) or overwrite:
            df.to_csv(outname, index=False)
            msg = 'wrote'
            if add:
                add_to_subject_set(subject_set_ids[wf], outname)
            else:
                print('add_to_subject_set(subject_set_ids["wf"], outname)')
        else:
            msg = 'not overwriting'
        print('{0:s} {1:s}'.format(msg, outname))

    return


def add_to_subject_set(subject_set_id, subject_set_file):
    """Import a 1 column file of subject_ids to a subject_set."""
    lines = []
    subject_set = SubjectSet.find(subject_set_id)
    with open(subject_set_file) as subject_ids:
        lines.append(subject_ids.read().splitlines())

    return subject_set.add(np.unique(lines))


def cull_wf1(classifications_filename, wf1_filename, overwrite=False):
    """Slice out all other workflows and maintain the header line."""
    if not os.path.isfile(wf1_filename) or overwrite:
        os.system('head -1 {0:s} > {1:s}'.format(classifications_filename,
                                                 wf1_filename))
        os.system('grep "Workflow 1: Identifying figure types" {0:s} >> {1:s}'
                  .format(classifications_filename, wf1_filename))
    return


def main(argv=None):
    """Main caller for workflow1to2"""
    parser = argparse.ArgumentParser(
        description="Add subject sets to workflow 2a,b,c from classifications")

    parser.add_argument('username', type=str, help='zooniverse username')

    parser.add_argument('password', type=str, help='password')

    parser.add_argument('-o', '--overwrite', action='store_true')
    parser.add_argument('-a', '--add', action='store_true')

    args = parser.parse_args(argv)
    # log in.
    Panoptes.connect(username=args.username, password=args.password)

    classifications_filename = 'astronomy-rewind-classifications.csv'
    wf1_filename = 'astronomy-rewind-classifications_wf1.csv'

    cull_wf1(classifications_filename, wf1_filename, overwrite=args.overwrite)
    cull_subject_ids(wf1_filename, overwrite=args.overwrite, add=args.add)


if __name__ == "__main__":
    sys.exit(main())
