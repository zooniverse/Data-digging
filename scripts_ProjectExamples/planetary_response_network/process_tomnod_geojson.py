import sys, os
import numpy as np
import pandas as pd
import ujson

dgfile = sys.argv[1]
outfile = dgfile.replace(".geojson", "_flattened_extracted.csv")
#dgfile = '/Users/vrooje/Downloads/digitalglobe_crowdsourcing_hurricane_irma_20170915/digitalglobe_crowdsourcing_hurricane_irma_20170915.geojson'
#outfile = '/Users/vrooje/Documents/Zooniverse/Zoomanitarian/Caribbean 2017/digitalglobe_crowdsourcing_hurricane_irma_20170915.json'

with open(dgfile) as json_data:
    dg = ujson.load(json_data)

    #print(dg)


try:
    del fmarks
except:
    pass


fmarks = open(outfile, "w")

fmarks.write("mark_id,overlay_id,other_id,map_id,created_at,user_id,tool,label,lon_mark,lat_mark,agreement,score,img_url\n")


# In [98]: dg.keys()
# Out[98]: [u'crs', u'type', u'features']
#
# In [99]: dg['crs']
# Out[99]: {u'properties': {u'name': u'urn:ogc:def:crs:OGC:1.3:CRS84'}, u'type': u'name'}
#
# In [100]: dg['type']
# Out[100]: u'FeatureCollection'
#
# dg['features'] is an array

marktype_each = [q['geometry']['type'] for q in dg['features']]
marktypes     = pd.Series(marktype_each).unique()


i_mark = 0
for feature in dg['features']:
    props = feature['properties']

    if (feature['geometry']['type']).lower() == 'point':
        i_mark += 1
        lon_mark = feature['geometry']['coordinates'][0]
        lat_mark = feature['geometry']['coordinates'][1]


        created_at = props['timestamp']
        img_date   = props['acquisition_date']
        sensor     = props['sensor']
        img_url    = props['chip_url']
        map_id     = props['map_id']
        overlay_id = props['overlay_id']
        catalog_id = props['catalog_id']
        other_id   = props['id']
        mark_id    = props['tag_id']
        user_id    = props['tagger_id']
        tool       = props['type_id']

        agreement  = props['agreement']
        score      = float(props['score'])
        label      = props['label']


        fmarks.write("%d,%d,\"%s\",%d,\"%s\",%d,%d,\"%s\",%f,%f,%d,%f,\"%s\"\n" % (mark_id,overlay_id,other_id,map_id,created_at,user_id,tool,label,lon_mark,lat_mark,agreement,score,img_url))


fmarks.close()
