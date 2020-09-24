# INPUT: CSV with the following columns:
#   lng_mean: Float, ex: -58.591
#   lat_mean: Float, ex: -52.161
#   polydict: Dictionary: ex: { lng: [-58.5931, -58.5933...], lat: [-52.1608, -52.1607...] }
# OUTPUT: JSON with the following format:
#   {
#     "type": "FeaturesCollection",
#       ...
#     "features": [
#       {
#          "type": "Feature",
#          "geometry": {
#            "type"
#            "coordinates": [3D array of lat/lon coordinates]
#          }
#       }
#     ]
#   }

import pandas as pd
import json
import string
from ast import literal_eval

def toGeoJSON():
    items = pd.read_csv("ffpoly_select.csv")
    items['polydict'] = [json.loads(q.replace("'", '"')) for q in items.polydict]

    geojson = {
        'type':'FeatureCollection',
        'crs': {
            'type': 'EPSG',
            'properties': {
                'code': 4326,
                'coordinate_order': [1, 0]
            }
        },
        'features':[]}

    for dict in items['polydict']:
        merged = [[a, b] for a, b in zip(dict['lng'], dict['lat'])]
        feature = {
            'type': 'Feature',
            "tippecanoe" : { "layer" : "kelp" },
            "properties": {
                "name": "Floating Forest Data"
            },
            'geometry': {
                'type': 'Polygon',
                'coordinates': [merged]
            },
            "style": {
                "fill":"red",
                "stroke-width":"3",
                "fill-opacity":0.6
            },
        }
        geojson['features'].append(feature)

    with open('kelp.json', 'w') as output_file:
        json.dump(geojson, output_file, indent=2)

toGeoJSON()
