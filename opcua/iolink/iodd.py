from dataclasses import dataclass, field
import logging
import os
import re
import xml.etree.ElementTree as ET

from information_node import InformationNode
from iodd_helpers import iodd_unitcodes
from settings import IODD_SCHEMA_LOC


@dataclass
class IODD:
    """Dataclass to store information about IODD files and their contents.

    Attributes
    ----------
    xml : str
        Location of the IODD file OR xml as a string
    family : list[str]
        Name of the sensor which is part of the IODD file
    information_nodes : list[InformationNode]
        List of InformationNode objects that are part of the sensor/IODD
    total_bit_length : int
        bit length of the sensor output

    Methods
    -------
    __post_init__:
        Parses data into object
    _parse_information_nodes:
        Parses information nodes into object
    _iodd_to_value_index:
        Converts bit information to useable value indices.
    """

    xml: str
    family: list[str] = field(default_factory=list)
    information_nodes: list[InformationNode] = field(default_factory=list)
    total_bit_length: int = None

    def __post_init__(self) -> None:
        """Parse data from the IODD file specified in the location variable."""
        root = self._get_root()

        device_variants = root.findall(
            f"./{IODD_SCHEMA_LOC}ProfileBody"
            f"/{IODD_SCHEMA_LOC}DeviceIdentity"
            f"/{IODD_SCHEMA_LOC}DeviceVariantCollection"
            f"/{IODD_SCHEMA_LOC}DeviceVariant"
        )
        texts = root.find(
            f"./{IODD_SCHEMA_LOC}ExternalTextCollection"
            f"/{IODD_SCHEMA_LOC}PrimaryLanguage"
        )
        variants = []
        for variant in device_variants:
            name = variant.find(f"./{IODD_SCHEMA_LOC}Name")
            text = texts.find(f"./{IODD_SCHEMA_LOC}Text[@id='{name.get('textId')}']")
            variants.append(text.get("value"))
        self.family = variants

        records = root.find(
            f"./{IODD_SCHEMA_LOC}ProfileBody"
            f"/{IODD_SCHEMA_LOC}DeviceFunction"
            f"/{IODD_SCHEMA_LOC}ProcessDataCollection"
            f"/{IODD_SCHEMA_LOC}ProcessData"
            f"/{IODD_SCHEMA_LOC}ProcessDataIn"
            f"/{IODD_SCHEMA_LOC}Datatype"
        )
        total_bit_length = int(records.get("bitLength"))
        self.total_bit_length = total_bit_length
        self._parse_information_nodes()
        self._iodd_to_value_index()

    def _get_root(self) -> ET.Element:
        """Get the root element of the IODD xml.

        :return: Root element
        """
        if os.path.exists(self.xml):
            tree = ET.parse(self.xml)
            root = tree.getroot()
        else:
            root = ET.fromstring(self.xml)
        return root

    def _parse_information_nodes(self) -> None:
        """Parse information points from IODD file to IODD object."""
        root = self._get_root()

        elements_with_unitcode = root.findall(f".//{IODD_SCHEMA_LOC}*[@unitCode]")
        unitcodes_input = []
        for element in elements_with_unitcode:
            unitcode = element.get("unitCode")
            if unitcode not in unitcodes_input:
                unitcodes_input.append(unitcode)
        dict_unit_codes_SI = iodd_unitcodes(unitcodes_input=unitcodes_input)
        logging.info(f"unit codes: {dict_unit_codes_SI}")
        # DeviceFunction element can be used as root for search for records and menus
        device_function = root.find(
            f"./{IODD_SCHEMA_LOC}ProfileBody/{IODD_SCHEMA_LOC}DeviceFunction"
        )

        # Searching for the root of records, menus and texts is better for readability
        records = device_function.find(
            f"./{IODD_SCHEMA_LOC}ProcessDataCollection"
            f"/{IODD_SCHEMA_LOC}ProcessData"
            f"/{IODD_SCHEMA_LOC}ProcessDataIn"
            f"/{IODD_SCHEMA_LOC}Datatype"
        )

        menus = device_function.findall(
            f"./{IODD_SCHEMA_LOC}UserInterface"
            f"/{IODD_SCHEMA_LOC}MenuCollection"
            f"/{IODD_SCHEMA_LOC}Menu"
        )

        texts = root.find(
            f"./{IODD_SCHEMA_LOC}ExternalTextCollection"
            f"/{IODD_SCHEMA_LOC}PrimaryLanguage"
        )

        datatypes = device_function.find(f"./{IODD_SCHEMA_LOC}DatatypeCollection")

        for idx, record in enumerate(records):
            name_node = record.find(f"./{IODD_SCHEMA_LOC}Name")
            nameid = name_node.get("textId")
            text = texts.find(f"./{IODD_SCHEMA_LOC}Text[@id='{nameid}']")
            name = text.get("value")
            bit_offset = int(record.get("bitOffset"))
            subindex = int(record.get("subindex"))

            # Some records might have a custom datatype, this accounts for that
            data = record.find(f"./{IODD_SCHEMA_LOC}SimpleDatatype")
            if data is None:
                datatype_ref = record.find(f"./{IODD_SCHEMA_LOC}DatatypeRef")
                datatype_id = datatype_ref.get("datatypeId")
                data = datatypes.find(
                    f".{IODD_SCHEMA_LOC}Datatype[@id='{datatype_id}']"
                )

            # boolean like datatypes have no bit length in their attributes, but are
            # represented by a 0 or 1 -> bit length is 1
            bit_length = data.get("bitLength")
            if bit_length is None:
                bit_length = 1
            else:
                bit_length = int(bit_length)

            information_node = InformationNode(
                name=name,
                bit_offset=bit_offset,
                bit_length=bit_length,
                subindex=subindex,
            )

            valueRange = data.find(f"./{IODD_SCHEMA_LOC}ValueRange")
            if valueRange is not None:
                low_val = int(valueRange.get("lowerValue"))
                up_val = int(valueRange.get("upperValue"))
                information_node.low_val = low_val
                information_node.up_val = up_val

            self.information_nodes.append(information_node)

        for menu in menus:
            if any(
                [
                    re.search(
                        f"^M_MR_SR_Observation(_[^_]*)?(_{unit})?$", menu.get("id")
                    )
                    for unit in dict_unit_codes_SI.keys()
                ]
            ):
                record_item_ref = menu.find(f"./{IODD_SCHEMA_LOC}RecordItemRef")
                if record_item_ref is None:
                    continue
                subindex = int(record_item_ref.get("subindex"))
                print('subindex: ', subindex)
                for idx, information_node in enumerate(self.information_nodes):
                    print('Information_node: ',information_node)
                    if information_node.subindex == subindex:
                        gradient = record_item_ref.get("gradient")
                        self.information_nodes[idx].gradient.append(
                            float(gradient) if gradient is not None else gradient
                        )
                        offset = record_item_ref.get("offset")
                        self.information_nodes[idx].offset.append(
                            float(offset) if offset is not None else offset
                        )
                        self.information_nodes[idx].display_format.append(
                            record_item_ref.get("displayFormat")
                        )
                        unitcode = record_item_ref.get("unitCode")
                        self.information_nodes[idx].unit_codes.append(
                            int(unitcode) if unitcode is not None else None
                        )
                        self.information_nodes[idx].units.append(
                            dict_unit_codes_SI[
                                int(unitcode) if unitcode is not None else None
                            ]
                        )
        # Some entries might not have a menu -> no way to read gradient, offset etc.
        # We will assume that these entries have values of 0 or 1. Then we can simply
        # set the missing bits to [None]
        for i, information_node in enumerate(self.information_nodes):
            if information_node.gradient == []:
                self.information_nodes[i].gradient = [None]
            if information_node.offset == []:
                self.information_nodes[i].offset = [None]
            if information_node.display_format == []:
                self.information_nodes[i].display_format = [None]
            if information_node.unit_codes == []:
                self.information_nodes[i].unit_codes = [None]
            if information_node.units == []:
                self.information_nodes[i].units = ["N/A"]

            self.information_nodes[i].convert_display_format()
            self.information_nodes[i].convert_bounds()

    def _iodd_to_value_index(self, block_length: int = 8) -> None:
        """Convert information about bit offset and length to useable indices.

        :param block_length: length of one block of bits, defaults to 8
        :return: IODD object with value indices added
        """
        for idx, ip in enumerate(self.information_nodes):
            bit_offset = ip.bit_offset
            bit_length = ip.bit_length
            if (bit_length % block_length == 0) and (bit_length >= block_length):
                num_indices = int(bit_length / block_length)
            else:
                num_indices = 1

            value_indices: list[int] = []
            start_index = int(
                (self.total_bit_length - (bit_offset + bit_length)) / block_length
            )
            for index in range(start_index, start_index + num_indices):
                value_indices.append(index)
            self.information_nodes[idx].value_indices = value_indices
