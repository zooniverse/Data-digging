import json
# import a module which is simply an instance of the class DBSCAN ie dbscan.py is a copy of class DBSCAN
# as usual the module must be in the current directory or in the sys path.
import dbscan

# data is just a list of [x,y]
data = [(629.1, 187.4), [636.5, 73.7], [474.4, 300.0], [541.7, 476.9], [544.9, 471.6],
        [529.1, 494.8, 'label'], (533.8, 473.2), [508.0, 362.1, 'label'], [485.9, 246.3], [484.9, 251.6],
        [370.1, 253.7], [604.7, 271.6], (607.0, 288.4), [603.8, 297.9], [719.6, 333.7]]

# determine a suitable eps and min_points
eps = 30
min_points = 3
print('epsilon =', eps, '  min_points =', min_points)
# and plug into a module containing an instance of class DBSCAN:
scan = dbscan.DBSCAN(eps, min_points)

# pass the data to the cluster function
scan.cluster(data)

# all done! Get the clustered data back:
print('clusters found:', scan.clusters)
print('number_of_clusters =', (len(scan.clusters)))
print('noise ie points in no cluster:', scan.noise)

# to save it in a known format convert to json strings.
# note subtle changes in brackets and quotes will occur!
clusters = json.dumps(scan.clusters)
noise = json.dumps(scan.noise)
print('ready to write clusters =', clusters)
print('ready to write noise =', noise)
