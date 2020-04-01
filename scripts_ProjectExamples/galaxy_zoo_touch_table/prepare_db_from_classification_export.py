#!/usr/bin/env python
import pandas as pd
import json
import string
from tqdm import tqdm as progress_bar
from itertools import cycle

def preprocessing():
    # Read the local CSV subject export
    classifications=pd.read_csv("classification-export.csv")

    classifications['metadata']=classifications['metadata'].apply(lambda x: json.loads(x))
    classifications['locations']=classifications['locations'].apply(lambda x: json.loads(x))

    # Include in subject_set_ids all subject sets you want to keep
    subject_set_ids = [];
    classifications = classifications.loc[classifications['subject_set_id'].isin(subject_set_ids)]

    classifications['smooth'] = 0;
    classifications['features'] = 0;
    classifications['star'] = 0;

    # Copy data from metadata into correct/new CSV headers with progress bar
    with progress_bar(total=len(classifications)) as current_progress:
        for index, row in classifications.iterrows():
            current_progress.update(1)
            for column in row['metadata']:
                # Find the Right Ascension and Declination in the metadata and assign to columns
                if column in ['ra', 'dec', '!ra', '!dec']:
                    stripped_punctuation = column.strip(string.punctuation)
                    classifications.loc[index, stripped_punctuation] = row['metadata'][column]
                # Find the image name, titled 'iauname', in the metadata and assign to a column
                if column in ['iauname', '!iauname']:
                    classifications.loc[index, 'filename'] = row['metadata'][column]
            for column in row['locations']:
                classifications.loc[index, 'image'] = row['locations'][column]

    # Drop unnecessary columns and rearrange
    classifications = classifications[['subject_id', 'classifications_count', 'ra', 'dec', 'image', 'filename', 'smooth', 'features', 'star']]

    # Create a parsed CSV for DB import
    classifications.to_csv('parsed-subject-set.csv',index = False,encoding='utf-8')

preprocessing()
