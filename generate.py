#!/usr/bin/env python3

# constants
ID_URL = "https://fahari.dhis2.savannahghi.org/api/system/id.json?limit=1000"


def fetch_new_ids():
    # TODO Generating IDs: https://fahari.dhis2.savannahghi.org/api/system/id.json?limit=1000
    # TODO Return ids
    pass

def read_facilities_csv_data():
    # TODO Read CSV data from facilities
    # TODO Return facilities
    pass

def generate_orgunit_metadata(facilities, ids):
    # TODO Generate facilities metadata
    # TODO Save to JSON
    pass

if __name__ == "__main__":
    # TODO Generate IDs
    ids = fetch_new_ids()
    facilities = read_facilities_csv_data()
    generate_orgunit_metadata(facilities, ids)
