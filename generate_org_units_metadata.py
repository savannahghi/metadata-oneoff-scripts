#!/usr/bin/env python
import json
import os
import pyexcel

from typing import (
    Any,
    Dict,
    Generator,
    Iterable,
    List,
    Optional,
    Sequence,
    Set,
    TypedDict
)


# =============================================================================
# TYPES
# =============================================================================

class CommonOrgUnitMeta(TypedDict):
    created: str
    lastUpdated: str
    openingDate: str


class ExcelOrgUnitData(TypedDict):
    County: str
    County_Code: str
    County_OUID: str
    Facility: str
    Facility_OUID: str
    MFL_Code: str
    Sub_County: str
    Sub_County_OUID: str
    Ward: str
    Ward_OUID: str


class ParentMeta(TypedDict):
    id: str


class PrimaryOrgUnitMeta(TypedDict):
    code: Optional[str]
    description: str
    id: str
    level: int
    name: str
    parent: Optional[ParentMeta]
    path: str
    shortName: str


class OrgUnitMeta(CommonOrgUnitMeta, PrimaryOrgUnitMeta):
    pass


# =============================================================================
# CONSTANTS
# =============================================================================

COMMON_ORG_UNIT_META: CommonOrgUnitMeta = {
    "created": "2021-09-13T12:02:16.925",
    "lastUpdated": "2021-09-13T18:51:24.461",
    "openingDate": "2021-04-23T00:00:00.000",
}

COUNTRY_META: PrimaryOrgUnitMeta = {
    "code": "KEN",
    "description": "The country Kenya",
    "id": "HfVjCurKxh2",
    "level": 1,
    "name": "Kenya",
    "parent": None,
    "path": "/HfVjCurKxh2",
    "shortName": "Kenya"
}

EXCEL_PATH: str = os.path.join(
    os.getcwd(),
    "DATIM Facility Hierarchy and OUIDs Kenya.xlsx"
)

JSON_OUTPUT_PATH: str = os.path.join(os.getcwd(), "org_units_metadata.json")

SUPPORTED_PSNUs_METAs: Sequence[PrimaryOrgUnitMeta] = (
    {
        "code": "ke2riftvalleykajiado",
        "description": "Kajiado County",
        "id": "iO2edHMzzoa",
        "level": 2,
        "name": "Kajiado County",
        "parent": {"id": COUNTRY_META["id"]},
        "path": f"/{COUNTRY_META['id']}/iO2edHMzzoa",
        "shortName": "Kajiado County"
    },
    {
        "code": "ke2nairobinairobicounty",
        "description": "Nairobi County",
        "id": "DW4iKNGrY42",
        "level": 2,
        "name": "Nairobi County",
        "parent": {"id": COUNTRY_META["id"]},
        "path": f"/{COUNTRY_META['id']}/DW4iKNGrY42",
        "shortName": "Nairobi County"
    },
)

SYSTEM_META = {
    "id": "cb1409e9-4d51-4689-bbfd-1b7a3eb17d4a",
    "rev": "a95cf40",
    "version": "2.36.3",
    "date": "2021-09-17T07:57:56.876"
}


# =============================================================================
# HELPERS
# =============================================================================

def _add_facility_if_non_existent(
    org_unit_data: ExcelOrgUnitData,
    existing_facilities_ids: Set[str],
    existing_org_units: List[OrgUnitMeta]
) -> None:
    if org_unit_data["Facility_OUID"] in existing_facilities_ids:
        # Nothing to do here, return to the caller
        return

    facility: OrgUnitMeta = {  # noqa
        **COMMON_ORG_UNIT_META,
        "code": str(org_unit_data["MFL_Code"]),
        "description": org_unit_data["Facility"],
        "id": org_unit_data["Facility_OUID"],
        "level": 5,
        "name": org_unit_data["Facility"],
        "parent": {"id": org_unit_data["Ward_OUID"]},
        "path": "/%s/%s/%s/%s/%s" % (
            COUNTRY_META["id"],
            org_unit_data["County_OUID"],
            org_unit_data["Sub_County_OUID"],
            org_unit_data["Ward_OUID"],
            org_unit_data["Facility_OUID"]
        ),
        "shortName": org_unit_data["Facility"]
    }
    existing_org_units.append(facility)
    existing_facilities_ids.add(facility["id"])


def _add_sub_county_if_non_existent(
    org_unit_data: ExcelOrgUnitData,
    existing_sub_counties_ids: Set[str],
    existing_org_units: List[OrgUnitMeta]
) -> None:
    if org_unit_data["Sub_County_OUID"] in existing_sub_counties_ids:
        # Nothing to do here, return to the caller
        return

    sub_county: OrgUnitMeta = {  # noqa
        **COMMON_ORG_UNIT_META,
        "code": None,
        "description": org_unit_data["Sub_County"],
        "id": org_unit_data["Sub_County_OUID"],
        "level": 3,
        "name": org_unit_data["Sub_County"],
        "parent": {"id": org_unit_data["County_OUID"]},
        "path": "/%s/%s/%s" % (
            COUNTRY_META["id"],
            org_unit_data["County_OUID"],
            org_unit_data["Sub_County_OUID"]
        ),
        "shortName": org_unit_data["Sub_County"]
    }
    existing_org_units.append(sub_county)
    existing_sub_counties_ids.add(sub_county["id"])


def _add_ward_if_non_existent(
    org_unit_data: ExcelOrgUnitData,
    existing_wards_ids: Set[str],
    existing_org_units: List[OrgUnitMeta]
) -> None:
    if org_unit_data["Ward_OUID"] in existing_wards_ids:
        # Nothing to do here, return to the caller
        return

    ward: OrgUnitMeta = {  # noqa
        **COMMON_ORG_UNIT_META,
        "code": None,
        "description": org_unit_data["Ward"],
        "id": org_unit_data["Ward_OUID"],
        "level": 4,
        "name": org_unit_data["Ward"],
        "parent": {"id": org_unit_data["Sub_County_OUID"]},
        "path": "/%s/%s/%s/%s" % (
            COUNTRY_META["id"],
            org_unit_data["County_OUID"],
            org_unit_data["Sub_County_OUID"],
            org_unit_data["Ward_OUID"]
        ),
        "shortName": org_unit_data["Ward"]
    }
    existing_org_units.append(ward)
    existing_wards_ids.add(ward["id"])


def read_org_units_data() -> Generator[ExcelOrgUnitData, None, None]:
    assert os.path.isfile(EXCEL_PATH), '"%s" is not a file.' % EXCEL_PATH
    org_units: Generator[ExcelOrgUnitData, None, None] = pyexcel.iget_records(
        file_name=EXCEL_PATH
    )
    return org_units


def generate_org_unit_metadata(
    org_units_data: Generator[ExcelOrgUnitData, None, None],
    supported_psnus: Sequence[PrimaryOrgUnitMeta],
) -> Dict[str, Any]:
    org_units = {
        "system": SYSTEM_META,
        "organisationUnits": []
    }
    facilities: Set[str] = set()
    sub_counties: Set[str] = set()
    wards: Set[str] = set()

    psnu_ids: Iterable[str] = tuple(map(lambda ou: ou["id"], supported_psnus))
    psnu_org_units_data: Iterable[ExcelOrgUnitData] = filter(
        lambda ou: ou["County_OUID"] in psnu_ids, org_units_data
    )

    # Add Country meta
    org_units["organisationUnits"].append(
        {
            **COMMON_ORG_UNIT_META,
            **COUNTRY_META
        },
    )

    # Add PSNUs Meta
    for psnu in supported_psnus:
        org_units["organisationUnits"].append(
            {
                **COMMON_ORG_UNIT_META,
                **psnu
            }
        )

    for org_unit_data in psnu_org_units_data:
        _add_sub_county_if_non_existent(
            org_unit_data,
            sub_counties,
            org_units["organisationUnits"]
        )
        _add_ward_if_non_existent(
            org_unit_data,
            wards,
            org_units["organisationUnits"]
        )
        _add_facility_if_non_existent(
            org_unit_data,
            facilities,
            org_units["organisationUnits"]
        )

    return org_units


def save_org_units_metadata(
    org_units_metadata: Dict[str, Any],
    out_file_path: str
) -> None:
    with open(out_file_path, "w") as json_output:
        json.dump(
            org_units_metadata,
            json_output,
            ensure_ascii=True,
            check_circular=True,
            indent=4,
            sort_keys=True
        )


# =============================================================================
# MAIN
# =============================================================================

if __name__ == '__main__':
    ous_data: Generator[ExcelOrgUnitData, None, None] = read_org_units_data()
    ous_meta: Dict[str, Any] = generate_org_unit_metadata(
        ous_data,
        SUPPORTED_PSNUs_METAs
    )
    save_org_units_metadata(ous_meta, out_file_path=JSON_OUTPUT_PATH)
    print("Done...")
