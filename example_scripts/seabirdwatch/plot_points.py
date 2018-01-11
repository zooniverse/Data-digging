import pandas
from panoptes_aggregation.csv_utils import unjson_dataframe
from skimage import io
import matplotlib.pyplot as plt
import progressbar
import numpy as np

# inputs
subjects_with_marks_path = 'subjects_with_marks.csv'
reducer_export_path = '251-reductions.csv'

widgets = [
    'Plotting: ',
    progressbar.Percentage(),
    ' ', progressbar.Bar(),
    ' ', progressbar.ETA()
]


def display_image_in_actual_size(im_data):
    dpi = 100
    height, width, depth = im_data.shape
    # What size does the figure need to be in inches to fit the image?
    figsize = width / float(dpi), height / float(dpi)
    # Create a figure of the right size with one axes that takes up the full figure
    fig = plt.figure(figsize=figsize)
    ax = fig.add_axes([0, 0, 1, 1])
    # Hide spines, ticks, etc.
    ax.axis('off')
    # Display the image.
    ax.imshow(im_data)
    return fig, ax


subjects = pandas.read_csv(subjects_with_marks_path)
reductions_all = pandas.read_csv(reducer_export_path)
reductions = reductions_all[reductions_all.reducer_key == 'points']
reductions = reductions.dropna(axis=1, how='all')
unjson_dataframe(reductions)
reductions_counts = reductions_all[reductions_all.reducer_key == 'counts']
reductions_counts = reductions_counts.dropna(axis=1, how='all')

bbox_props = {
    'boxstyle': 'round',
    'fc': 'w',
    'ec': '0.5',
    'alpha': 1
}
text_props = {
    'bbox': bbox_props,
    'ha': 'left',
    'va': 'top',
    'size': 18
}

UK_sites = [
    'PUFF',
    'RATH',
    'SKOM',
    'SKEL'
]

udx = np.array([np.any([u in s for u in UK_sites]) for s in subjects.site_id])

pbar = progressbar.ProgressBar(widgets=widgets, max_value=udx.sum())
pbar.start()
ct = 0
for _, subject in subjects[udx].iterrows():
    sdx = (reductions.subject_id == subject.subject_id)
    rdx = (reductions_counts.subject_id == subject.subject_id)
    number_classifications = reductions_counts[rdx].iloc[0]['data.classifications']
    if number_classifications >= 10:
        reduction = reductions[sdx].iloc[0]
        image = io.imread(subject.url)
        fig, ax = display_image_in_actual_size(image)
        text = ['Number of Classifications: {0}'.format(number_classifications)]
        if isinstance(reduction['data.T3_tool0_clusters_count'], list):
            ax.plot(reduction['data.T3_tool0_clusters_x'], reduction['data.T3_tool0_clusters_y'], 'o', ms=20, mec='C8', mew=3, mfc='none')
            text.append('Number of Kittiwakes: {0}'.format(len(reduction['data.T3_tool0_clusters_count'])))
        if isinstance(reduction['data.T3_tool1_clusters_count'], list):
            ax.plot(reduction['data.T3_tool1_clusters_x'], reduction['data.T3_tool1_clusters_y'], 'o', ms=20, mec='C0', mew=3, mfc='none')
            text.append('Number of Guillemots: {0}'.format(len(reduction['data.T3_tool1_clusters_count'])))
        if isinstance(reduction['data.T3_tool2_clusters_count'], list):
            ax.plot(reduction['data.T3_tool2_clusters_x'], reduction['data.T3_tool2_clusters_y'], 'o', ms=20, mec='C6', mew=3, mfc='none')
            text.append('Number of Chicks: {0}'.format(len(reduction['data.T3_tool2_clusters_count'])))
        if isinstance(reduction['data.T3_tool3_clusters_count'], list):
            ax.plot(reduction['data.T3_tool3_clusters_x'], reduction['data.T3_tool3_clusters_y'], 'o', ms=20, mec='C2', mew=3, mfc='none')
            text.append('Number of Others: {0}'.format(len(reduction['data.T3_tool3_clusters_count'])))
        ax.text(10, 10, '\n'.join(text), **text_props)
        fig.savefig('images/{0}_{1}.png'.format(subject.site_id, subject.subject_id))
        plt.close(fig)
    ct += 1
    pbar.update(ct)
pbar.finish()
