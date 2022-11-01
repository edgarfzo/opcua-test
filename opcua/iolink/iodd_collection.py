import logging
import os

from iolink.iodd import IODD
from iolink.errors import ConflictingIODDsFoundError


class IODDCollection:
    """Manages the IODD file collection and provides IODDs.

    Attributes
    ----------
    iodds : list[IODD]
        List of IODD objects currently managed
    location : str
        Location of the IODD collection

    Methods
    -------
    from_json
    from_local

    """

    _logger = logging.getLogger("IODDCollection")

    def __init__(
        self,
        location: str | list[str] = ["database", "collection"],
        load_on_init: bool = True,
    ) -> None:
        """Create an IODDCollection.

        :param location: relative location of the collection,
        defaults to "database/collection"
        :param load_on_init: Whether to load the IODD collection from the location on
        initialization, defaults to True
        """
        if isinstance(location, list):
            location = os.path.normpath(os.path.join(*location))
        self._iodds: list[IODD] = []
        self._location = os.path.normpath(os.path.join(os.getcwd(), location))
        if not os.path.exists(self._location):
            os.mkdir(self._location)
        if load_on_init:
            self.from_local()

    @property
    def iodds(self) -> list[IODD]:
        """Get IODDs in collection."""
        return self._iodds

    @property
    def location(self) -> str:
        """Get IODD collection location."""
        return self._location

    def add_iodd(self, iodd: IODD) -> None:
        """Add a new IODD to the IODDCollection.

        :param iodd: IODD to add
        """
        self._iodds.append(iodd)

    def from_json(self, json: list[dict]) -> None:
        """Load IODDs from file locations specified in provided json.

        :param json: JSON like list with dictionaries that have a key-value pair of
        "file_loc": Full path to file
        """
        self._iodds = [IODD(entry["file_loc"]) for entry in json]

    def from_local(self) -> None:
        """Load the IODDs from the location into memory."""
        iodds: list[IODD] = []
        for f in os.listdir(self._location):
            if not f.endswith("IODD1.1.xml"):
                continue
            iodds.append(IODD(xml=os.path.join(self._location, f)))
        self._iodds = iodds

    def lookup_sensor(self, sensor: str) -> IODD | None:
        """Look up sensor in the IODDCollection object.

        :param sensor: Name of the sensor to look up
        :raises ConflictingIODDsFoundError: Raised if multiple IODDs are found with the
        same sensor in their family
        :return: IODD of the sensor or None if no IODD found in collection
        """
        iodd = [item for item in self.iodds if sensor in item.family]
        if len(iodd) == 0:
            return None
        elif len(iodd) == 1:
            return iodd[0]
        else:
            raise ConflictingIODDsFoundError(sensor, iodd)
