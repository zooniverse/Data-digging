import argparse
import io
from panoptes_client import Panoptes, Subject, Project, SubjectSet
import os, sys, getopt, urllib, json, csv
import json
import requests
import typing


class GeolocateClientError(Exception):
    pass


class GeolocateClient:
    def __init__(self, debug=False):
        self.endpoint = "http://www.geo-locate.org/webservices/geolocatesvcv2/glcwrap.aspx"

    def georef(self, locality, country, stateProv, county, hwyX=True, enableH2O=True, doUncert=True, doPoly=False, displacePoly=False, languageKey=0):
        params = {'country': country, 'locality': locality, 'state': stateProv, 'county':county, 'hwyX':str(hwyX),'enableH2O':str(enableH2O), 'doUncert':str(doUncert), 'doPoly':str(doPoly), 'displacePoly': str(displacePoly), 'languageKey':str(languageKey), 'fmt':'json'}
        try:
            response = requests.get(self.endpoint, params=params)
            response.raise_for_status()
            json_response = response.json()
            return json_response
        except requests.exceptions.RequestException as exc:
            raise GeolocateClientError from exc


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="nfn_create_geojson_subjects",
        description="Create geolocate subjects with json media files"
    )
    parser.add_argument("csv_file", help="csv file to create subjects for", type=argparse.FileType("r", encoding="utf-8"))
    parser.add_argument("-u", "--username", help="Panoptes Username", required=True, type=str)
    parser.add_argument("-p", "--password", help="Panoptes password", type=str)
    parser.add_argument("-pid", "--project_id", help="Panoptes Project Id", type=int, required=True)
    parser.add_argument("-ssid", "--subject_set_id", help="Panoptes Subject Set Id", type=int, required=True)

    args = parser.parse_args()
    glc = GeolocateClient()
    reader = csv.DictReader(args.csv_file)
    panoptes_client = Panoptes()
    panoptes_client.connect(
        username=args.username,
        password=args.password,
    )
    project = Project(args.project_id)
    subject_set = SubjectSet(args.subject_set_id)
    subjects_count = 0
    for row_number, row in enumerate(reader, start=1):
        try:
            json_result = glc.georef(
                locality=row['data:locality'],
                stateProv=row['data:stateProvince'],
                country=row['data:country'],
                county=row['data:county']
            )

            if json_result['numResults'] == 0:
                raise GeolocateClientError(f'No results found for CSV row number {row_number}\n')

            first_glc_result = json_result['resultSet']['features'][0]
            transformed_glc_result = first_glc_result.copy()
            transformed_glc_result['properties'] = transformed_glc_result['properties'].copy()
            uncertainty_radius = transformed_glc_result['properties'].pop('uncertaintyRadiusMeters', None)
            if uncertainty_radius == 'Unavailable':
                uncertainty_radius = None
            transformed_glc_result['properties']['uncertainty_radius'] = uncertainty_radius
            subject = Subject()
            subject.links.project = project
            reference_data = {
                'locality':row['data:locality'],
                'stateprovince':row['data:stateProvince'],
                'country':row['data:country'],
                'county':row['data:county']
            }
            glc_subject_json = {
                'type': 'FeatureCollection',
                'features': [
                    transformed_glc_result
                ],
                'reference_data': reference_data
            }
            glc_subj_json_str = json.dumps(glc_subject_json)

            bio = io.BytesIO(glc_subj_json_str.encode('utf-8'))
            subject.add_location(bio, manual_mimetype='application/json')
            subject.save()
            subject_set.add(subject)
            subjects_count += 1
        except GeolocateClientError as glc_e:
            sys.stderr.write(f"API error on row: {row_number}\n {glc_e}\n")
            continue
        except Exception as e:
            print(f"Error reading CSV on row: {row_number} with error {e}\n")
            continue
    print(f"{subjects_count} GeoJson Subjects Created")
