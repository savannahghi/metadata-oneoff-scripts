#!/usr/bin/env python3
import csv
import json
import os

from constants import CODES

# constants
ID_URL = "https://fahari.dhis2.savannahghi.org/api/system/id.json?limit=1000"
CSV_PATH = os.path.join(os.getcwd(), "facilities.csv")
JSON_OUTPUT_PATH = os.path.join(os.getcwd(), "generated_facility_metadata.json")

assert os.path.isfile(CSV_PATH)


def read_facilities_csv_data():
    facilities = []
    with open(CSV_PATH, "r") as csv_file:
        records = csv.DictReader(csv_file)
        for r in records:
            facilities.append(r)

    return facilities


def generate_orgunit_metadata(facilities, ids):
    org_units = {
        "system": {
            "id": "cb1409e9-4d51-4689-bbfd-1b7a3eb17d4a",
            "rev": "a95cf40",
            "version": "2.36.3",
            "date": "2021-09-17T07:57:56.876"
        },
        "organisationUnits": []
    }
    for facility, new_id in zip(facilities, ids[: len(facilities)]):
        basePath = ""
        parent = ""
        if facility["county"] == "Kajiado":
            parent = "DsIxJvZplZz"
            basePath = f"/YoEaChfYlbo/{parent}/"
        else:
            parent = "ERlzhW0dJw9"
            basePath = f"/YoEaChfYlbo/{parent}/"

        metadata = {
            "code": facility["mfl_code"],
            "level": 2,
            "created": "2021-09-13T18:54:59.224",
            "lastUpdated": "2021-09-13T18:54:59.249",
            "name": facility["name"],
            "id": new_id,
            "shortName": facility["name"][:24],
            "description": facility["name"],
            "path": f"{basePath}{new_id}",
            "openingDate": "2021-04-23T00:00:00.000",
            "parent": {
                "id": parent,
            },
            "lastUpdatedBy": {
                "displayName": "Daniel Nyaga",
                "name": "Daniel Nyaga",
                "id": "bF8LjqfTQjJ",
                "username": "ngurenyaga",
            },
            "createdBy": {
                "displayName": "Daniel Nyaga",
                "name": "Daniel Nyaga",
                "id": "bF8LjqfTQjJ",
                "username": "ngurenyaga",
            },
            "attributeValues": [],
            "translations": [],
        }
        org_units["organisationUnits"].append(metadata)

    with open(JSON_OUTPUT_PATH, "w") as json_output:
        json.dump(
            org_units,
            json_output,
            ensure_ascii=True,
            check_circular=True,
            indent=4,
            sort_keys=True,
        )
        print("written JSON output")


if __name__ == "__main__":
    facilities = read_facilities_csv_data()
    generate_orgunit_metadata(facilities, CODES)
