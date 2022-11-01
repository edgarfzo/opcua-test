class IODDNotFoundError(Exception):
    """Exception raised when IODD could not be found in IODDFinder."""

    def __init__(self, sensor: str) -> None:
        """Create IODDNotFoundError object.

        :param sensor: name of the sensor that is missing an IODD
        """
        self.sensor = sensor
        self.msg = f"IODD for sensor {self.sensor} not found in IODDFinder"
        super().__init__(self.msg)


class ConflictingIODDsFoundError(Exception):
    """Exception raised for when multiple IODDs have the same sensor in their family."""

    def __init__(self, sensor: str, iodd_files: list[str]) -> None:
        """Create ConflictingIODDsFoundError object.

        :param sensor: name of the sensor that has multiple IODDs
        :param iodd_files: location of the conflicting IODDs
        """
        self.sensor = sensor
        self.iodd_files = iodd_files
        self.msg = (
            f"Found multiple IODDs that contain sensor {sensor} in their families: \n"
            "\n".join(iodd_files)
        )
        super().__init__(self.msg)
