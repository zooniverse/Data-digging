import pandas
from panoptes_aggregation.csv_utils import unjson_dataframe
from pprint import pprint
import progressbar
from collections import OrderedDict

# inputs
subject_export_path = 'seabirdwatch-subjects.csv'
reducer_export_path = '251-reductions.csv'

# ouptputs
subjects_with_marks_path = 'subjects_with_marks.csv'
brids_over_time_path = 'all_birds_over_time.csv'
counts_by_region = 'bird_count.txt'

widgets = [
    'Counting: ',
    progressbar.Percentage(),
    ' ', progressbar.Bar(),
    ' ', progressbar.ETA()
]

subjects_with_marks = {
    'subject_id': [],
    'url': [],
    'site_id': []
}
counts = {}
counts_with_date = OrderedDict([
    ('site', []),
    ('date', []),
    ('file_name', []),
    ('kittiwakes', []),
    ('guillemots', []),
    ('chicks', []),
    ('others', [])
])
input_type = 'online'

subjects = pandas.read_csv(subject_export_path)
subjects['metadata'] = subjects['metadata'].apply(eval)
subjects['locations'] = subjects['locations'].apply(eval)

subject_dates = pandas.read_csv('seabird_data_subject_times.csv')
subject_dates.create_date = pandas.to_datetime(subject_dates.create_date, format='%Y:%m:%d %H:%M:%S')

reductions_all = pandas.read_csv(reducer_export_path)
reductions = reductions_all[reductions_all.reducer_key == 'points']
reductions = reductions.dropna(axis=1, how='all')
unjson_dataframe(reductions)

reductions_counts = reductions_all[reductions_all.reducer_key == 'counts']
reductions_counts = reductions_counts.dropna(axis=1, how='all')

reductions_dark = reductions_all[reductions_all.reducer_key == 'too_dark']
reductions_dark = reductions_dark.dropna(axis=1, how='all')


pbar = progressbar.ProgressBar(widgets=widgets, max_value=len(reductions))
pbar.start()
ct = 0
for _, reduction in reductions.iterrows():
    sdx = (subjects.subject_id == reduction.subject_id) & (subjects.workflow_id == 251)
    site_id = subjects.metadata[sdx].iloc[0]['image_id'].split('_')[0]
    counts[site_id] = counts.get(site_id, {})
    marked = False
    rdx = (reductions_counts.subject_id == reduction.subject_id)
    number_classifications = reductions_counts[rdx].iloc[0]['data.classifications']
    counts[site_id]['classifications'] = counts[site_id].get('classifications', 0) + number_classifications
    ddx = (reductions_dark.subject_id == reduction.subject_id)
    number_dark = reductions_dark[ddx].iloc[0]['data.num_votes']
    counts[site_id]['dark'] = counts[site_id].get('dark', 0) + number_dark
    ct_k = 0
    if ('data.T3_tool0_clusters_count' in reduction) and isinstance(reduction['data.T3_tool0_clusters_count'], list):
        ct_k = len(reduction['data.T3_tool0_clusters_count'])
        counts[site_id]['kittiwakes'] = counts[site_id].get('kittiwakes', 0) + ct_k
        if ct_k > 0:
            marked = True
    ct_g = 0
    if ('data.T3_tool1_clusters_count' in reduction) and isinstance(reduction['data.T3_tool1_clusters_count'], list):
        ct_g = len(reduction['data.T3_tool1_clusters_count'])
        counts[site_id]['guillemots'] = counts[site_id].get('guillemots', 0) + ct_g
        if ct_g > 0:
            marked = True
    ct_c = 0
    if ('data.T3_tool2_clusters_count' in reduction) and isinstance(reduction['data.T3_tool2_clusters_count'], list):
        ct_c = len(reduction['data.T3_tool2_clusters_count'])
        counts[site_id]['chicks'] = counts[site_id].get('chicks', 0) + ct_c
        if ct_c > 0:
            marked = True
    ct_o = 0
    if ('data.T3_tool3_clusters_count' in reduction) and isinstance(reduction['data.T3_tool3_clusters_count'], list):
        ct_o = len(reduction['data.T3_tool3_clusters_count'])
        counts[site_id]['other'] = counts[site_id].get('other', 0) + ct_o
        if ct_o > 0:
            marked = True
    if marked:
        subjects_with_marks['subject_id'].append(reduction.subject_id)
        subjects_with_marks['url'].append(subjects[sdx].iloc[0].locations['0'])
        subjects_with_marks['site_id'].append(site_id)
        ddx = (subject_dates.file_name == subjects[sdx].iloc[0].locations['0'].split('/')[-1])
        counts_with_date['site'].append(site_id[:4])
        counts_with_date['date'].append(subject_dates[ddx].create_date.iloc[0])
        counts_with_date['file_name'].append(subject_dates[ddx].file_name.iloc[0])
        counts_with_date['kittiwakes'].append(ct_k)
        counts_with_date['guillemots'].append(ct_g)
        counts_with_date['chicks'].append(ct_c)
        counts_with_date['others'].append(ct_o)
    ct += 1
    pbar.update(ct)
pbar.finish()

pandas.DataFrame(subjects_with_marks).to_csv(subjects_with_marks_path, index=False)
pandas.DataFrame(counts_with_date).to_csv(brids_over_time_path, index=False)

with open(counts_by_region, 'w') as file_out:
    pprint(counts, stream=file_out)
