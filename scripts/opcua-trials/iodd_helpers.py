import logging
import os
import xml.etree.ElementTree as ET

from settings import IODD_SCHEMA_LOC


def iodd_unitcodes(unitcodes_input: list, loc: str = "") -> list:
    r"""Associate unitcodes with their respective abbreviations.

    :param unitcodes_input: list of unitcodes used in a given IODD
    :param loc: location of the IODD-StandardUnitDefinitions*.xml file,
                defaults to ".\iodd\IODD-StandardUnitDefinitions1.1.xml"
    :return: list of dicts with used unitcodes
    """
    if not os.path.exists(
        os.path.join(os.getcwd(), loc, "IODD-StandardUnitDefinitions1.1.xml")
    ):
        raise FileNotFoundError(
            "IODD StandardUnitDefinitions file not found at: "
            f"{os.path.join(os.getcwd(), loc)}"
        )
    tree = ET.parse(os.path.join(loc, "IODD-StandardUnitDefinitions1.1.xml"))
    root = tree.getroot()

    iodd_units_version = root.find(f"./{IODD_SCHEMA_LOC}DocumentInfo")
    logging.debug(
        "IODD-StandardUnitDefinitions version " f"{iodd_units_version.get('version')}"
    )

    unitcodes_output = {}
    for unitcode in unitcodes_input:
        if unitcode is not None:
            unit = root.find(
                f"./{IODD_SCHEMA_LOC}UnitCollection"
                f"/{IODD_SCHEMA_LOC}Unit[@code='{unitcode}']"
            )
            unitcodes_output[int(unit.get("code"))] = unit.get("abbr")

    # Some variables might have unitcode "None", therefore we will manually add an entry
    # We ignored "None" from the input so that we don't have to handle errors from the
    # XML parser
    unitcodes_output[None] = "N/A"

    return unitcodes_output
