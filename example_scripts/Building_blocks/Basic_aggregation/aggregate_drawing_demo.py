import csv
import sys
import json
import dbscan

csv.field_size_limit(sys.maxsize)
# set up the file locations (user specific)
location = r'C:\py\Data_digging\sorted_flattened-points_demo.csv'
locationselect = r'C:\py\Data_digging\aggregate_drawing_demo.csv'


def process_aggregation(subj, image, clas, ep, min_point, h_palms, flowring, leafles):
    if clas > 10: # test for a minimum of 10 valid clssifications   
        scanh = dbscan.DBSCAN(ep, min_point)
        scanh.cluster(h_palms)
        hc_p = json.dumps(scanh.points)
        count_h = len(scanh.points)
        hclusters = json.dumps(scanh.clusters)
        hnoise = json.dumps(scanh.noise)
        scanf = dbscan.DBSCAN(ep, min_point)
        scanf.cluster(flowring)
        fc_p = json.dumps(scanf.points)
        count_f = len(scanf.points)
        fclusters = json.dumps(scanf.clusters)
        fnoise = json.dumps(scanf.noise)
        scanl = dbscan.DBSCAN(ep, min_point)
        scanl.cluster(leafles)
        lc_p = json.dumps(scanl.points)
        count_l = len(scanl.points)
        lclusters = json.dumps(scanl.clusters)
        lnoise = json.dumps(scanl.noise)
        print(subject)
        new_row = {'subject_ids': subj, 'image_number': image, 'classifications': i,
                   'Count_h_palms': count_h, 'H_palm_clusters': hc_p, 'Hclusters': hclusters,
                   'Hnoise': hnoise, 'Count_flowering': count_f, 'flowering_clusters': fc_p,
                   'fclusters': fclusters, 'fnoise': fnoise, 'Count_leafless': count_l,
                   'leafless_clusters': lc_p, 'lclusters': lclusters, 'lnoise': lnoise}
        writer.writerow(new_row)
        return True
    else: 
        return False

# set up the output file names for the aggregated and clustered data points
with open(locationselect, 'w', newline='') as file:
    fieldnames = ['subject_ids', 'image_number', 'classifications',
                  'Count_h_palms', 'H_palm_clusters', 'Hclusters', 'Hnoise',
                  'Count_flowering', 'flowering_clusters', 'fclusters', 'fnoise',
                  'Count_leafless', 'leafless_clusters', 'lclusters', 'lnoise']
    writer = csv.DictWriter(file, fieldnames=fieldnames)
    writer.writeheader()

    # set up to read the flattened file
    with open(location) as f:
        r = csv.DictReader(f)

        # set some parameters for the clustering criteria
        cluster_radius = 60
        min_points = 5

        # initialize a starting point subject and empty bins for aggregation
        subject = ''
        image_number = ''
        eps = cluster_radius
        i = 1
        h_palm = []
        flowering = []
        leafless = []

        # Loop over the flattened classification records
        for row in r:
            # read a row and pullout the flattened data fields we need to aggregate, or output.
            new_subject = row['subject_ids']
            new_image_number = row['image_number']
            new_user = row['user_name']
            row_H_palm = json.loads(row['H palm'])
            row_flowering = json.loads(row['flowering'])
            row_leafless = json.loads(row['leafless'])
            image_size = json.loads(row['image_size'])
            new_eps = int(cluster_radius * int(image_size[0]) / 2000 + .5)

            # test for change in selector - output on change
            if new_subject != subject:
                if i != 1:  # if not the first line analyse the aggregated fields and output the results
                    process_aggregation(subject, image_number, i, eps, min_points, h_palm, flowering, leafless)

                # reset the selector, those things we need to output and the bins for the aggregation.
                i = 1
                subject = new_subject
                image_number = new_image_number
                users = {new_user}
                eps = new_eps
                h_palm = row_H_palm
                flowering = row_flowering
                leafless = row_leafless

            else:
                 # do the aggregation - clean for excess classifications and multiple classifications by the same
                # user on this subject
                if users != users | {new_user} and i <= 15:
                    users |= {new_user}
                    h_palm.extend(row_H_palm)
                    flowering.extend(row_flowering)
                    leafless.extend(row_leafless)
                    eps = int(cluster_radius * int(image_size[0]) / 2000 + .5)
                    i += 1

        # catch and process the last aggregated group
        process_aggregation(subject, image_number, i, eps, min_points, h_palm, flowering, leafless)
