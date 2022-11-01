class InformationNode:
    """Dataclass to store information about an information point.

    An information point describes a singular output value of a sensor and how the raw
    data from the OPC-UA server needs to be processed.

    Attributes
    ----------
    name : str
        Name of the information point
    bit_offset : int
        offset from the right side of the bit-wise sensor output for a specific
        information point in bits
    bit_length : int
        length of the bit-wise sensor output for a specific information point in bits
    subindex : int
        used for indexing inside the IODD
    low_val : int
        lower bound for the bit values
    up_val : int
        upper bound for the bit values
    gradient : float
        factor for converting from bits to real values
    offset : float
        offset for converting from bits to real values
    display_format : str
        format for the real values
    unit_code : int
        IODD Standard Unit Definitions unit code for the unit of the real sensor output
    units : str
        abbreviation of the real sensor values unit
    value_indices : list[int]
        indices for getting the correct bit values from the sensor output

    Methods
    -------
    byte_to_real_value:
        Uses the conversion information to convert the byte value from the OPC UA server
        to real values
    convert_bounds:
        Converts the lower and upper bounds by using conversion information
    convert_display_format
        Converts the display format to an integer that can be used by the builtin
        round() function
    """

    def __init__(
        self,
        name: str,
        bit_offset: int,
        bit_length: int,
        subindex: int,
    ) -> None:
        """Create InformationNode object.

        :param name: Name of the information node
        :param bit_offset: right hand offset of the information nodes values in bit of
        the byte value array
        :param bit_length: length in bit of the information nodes values of the byte
        value array
        :param subindex: subindex of the information node within the IODD
        """
        self.name = name
        self.bit_offset = bit_offset
        self.bit_length = bit_length
        self.subindex = subindex
        self.low_val = None
        self.up_val = None
        self.low_bounds = []
        self.up_bounds = []
        self.gradient = []
        self.offset = []
        self.display_format = []
        self.unit_codes = []
        self.units = []
        self.value_indices = []

    def __repr__(self) -> str:
        """Represent the object as a string.

        :return: Representation string
        """
        attribute_string = "\n - ".join(
            [f"{key}: {val}" for key, val in self.__dict__.items()]
        )
        return f"InformationNode {self.name}: \n - {attribute_string}"

    def byte_to_real_value(
        self, byte_values: list[int], byteorder: str = "big", signed: bool = True
    ) -> list[float]:
        """Convert byte value of a sensor reading to real value.

        :param byte_values: List of byte values to convert
        :param byteorder: Indicate the order of byte values. If byte order is big, the
        most significant byte is at the beginning of the list, defaults to "big"
        :param signed: Whether the bytes are signed or not, defaults to True
        """
        # Special case for values that take up less than one 8-bit block
        # We are going to assume that these values don't have different possible units
        if (self.bit_length % 8 != 0) and (len(self.value_indices) == 1):
            byte_value = int.from_bytes(
                [byte_values[i] for i in self.value_indices],
                byteorder=byteorder,
                signed=signed,
            )
            bit_list = [1 if byte_value & (1 << (7 - n)) else 0 for n in range(8)]
            start_index = 8 - (self.bit_offset + self.bit_length)
            end_index = start_index + self.bit_length
            return [int("".join(str(i) for i in bit_list[start_index:end_index]), 2)]

        if self.gradient == [None]:
            gradient = [1]
        else:
            gradient = self.gradient

        if self.offset == [None]:
            offset = [0]
        else:
            offset = self.offset
        values = [
            int.from_bytes(
                [byte_values[i] for i in self.value_indices],
                byteorder=byteorder,
                signed=signed,
            )
            * gradient[j]
            + offset[j]
            for j, _ in enumerate(gradient)
        ]
        for i, display_format in enumerate(self.display_format):
            if display_format is not None:
                values[i] = round(values[i], display_format)
        return [float(v) for v in values]

    def convert_bounds(self) -> None:
        """Convert lower and upper bounds to real values instead of byte values."""
        if (
            (self.low_val is not None)
            and (self.gradient != [None])
            and (self.offset != [None])
        ):
            for i, _ in enumerate(self.gradient):
                self.low_bounds.append(
                    round(
                        self.low_val * self.gradient[i] + self.offset[i],
                        self.display_format[i],
                    )
                )
        else:
            self.low_bounds = [-1]
        if (
            (self.up_val is not None)
            and (self.gradient != [None])
            and (self.offset != [None])
        ):
            for i, _ in enumerate(self.gradient):
                self.up_bounds.append(
                    round(
                        self.up_val * self.gradient[i] + self.offset[i],
                        self.display_format[i],
                    )
                )
        else:
            self.up_bounds = [-1]

    def convert_display_format(self) -> None:
        """Convert display format to integer.

        Display format comes in the form of "Dec.X", where X is the number of decimals
        Converting this into an int allows easier usage later for rounding
        """
        for i, _ in enumerate(self.display_format):
            if self.display_format[i] is not None:
                self.display_format[i] = int(self.display_format[i].split(".")[1])

    def fill_for_testing(self) -> None:
        """Set the Information Node up to be usable with no actual information.

        Convenience method for testing purposes.
        """
        self.low_bounds.append(None)
        self.up_bounds.append(None)
        self.gradient.append(None)
        self.offset.append(None)
        self.display_format.append(None)
        self.unit_codes.append(None)
        self.units.append(None)
        self.value_indices.append(0)
