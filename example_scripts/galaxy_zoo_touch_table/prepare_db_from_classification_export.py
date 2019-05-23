#!/usr/bin/env python
import pandas as pd
import json
import string
from tqdm import tqdm
from itertools import cycle

def preprocessing():
    # Read the local CSV subject export
    classifications=pd.read_csv("classification-export.csv")

    classifications['metadata']=classifications['metadata'].map(lambda x: json.loads(x))
    classifications['locations']=classifications['locations'].map(lambda x: json.loads(x))

    # Include in subject_set_ids all subject sets you want to keep
    subject_set_ids = [];
    classifications = classifications.loc[classifications['subject_set_id'].isin(subject_set_ids)]

    classifications['smooth'] = 0;
    classifications['features'] = 0;
    classifications['star'] = 0;

    # Copy data from metadata into correct/new CSV headers with progress bar
    with tqdm(total=len(classifications)) as pbar:
        for index, row in classifications.iterrows():
            pbar.update(1)
            for column in row['metadata']:
                if column in ['ra', 'dec', '!ra', '!dec']:
                    strippedPunctuation = column.strip(string.punctuation)
                    classifications.loc[index, strippedPunctuation] = row['metadata'][column]
            for column in row['locations']:
                classifications.loc[index, 'image'] = row['locations'][column]

    # Drop unnecessary columns and rearrange
    classifications = classifications[['subject_id', 'classifications_count', 'ra', 'dec', 'image', 'smooth', 'features', 'star']]

    # Create a parsed CSV for DB import
    classifications.to_csv('parsed-subject-set.csv',sep=',',index = False,encoding='utf-8')

preprocessing()
