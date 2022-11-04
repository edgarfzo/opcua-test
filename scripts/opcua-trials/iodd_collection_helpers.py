import logging
import os
import re
import sqlite3
import time
from zipfile import ZipFile

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service

from iolink.iodd import IODD
from iolink.errors import IODDNotFoundError
from iolink.iodd_collection import IODDCollection


def ensure_collection_exists(conn: sqlite3.Connection, cur: sqlite3.Cursor) -> None:
    """Ensure that the collection table exists in the database.

    :param conn: Connection object that points to database which houses the collection
    :param cur: Cursor object used for executing queries
    """
    _logger = logging.getLogger("IODDCollection")
    try:
        cur.execute("create table ioddcollection(family stringlist, file_loc string)")
        conn.commit()
    except sqlite3.OperationalError:
        _logger.info("IODD collection index already exists")
    update_from_collection_folder(conn=conn, cur=cur)


def save(
    collection: IODDCollection,
    conn: sqlite3.Connection,
    cur: sqlite3.Cursor,
    overwrite: bool = True,
) -> None:
    """Save the IODDCollection to the database.

    :param collection: IODDCollection to be saved.
    :param conn: Connection object that points to database which houses the collection
    :param cur: Cursor object used for executing queries
    :param overwrite: Whether to overwrite the existing index, defaults to True
    """
    _logger = logging.getLogger("IODDCollection")
    if overwrite:
        cur.execute("delete from ioddcollection")

    for iodd in collection.iodds:
        family_str = ",".join(iodd.family)
        query = f"insert into ioddcollection values ('{family_str}', " f"'{iodd.xml}')"
        cur.execute(query)
    conn.commit()
    _logger.debug("Saved index to database")


def scrape(
    sensor: str,
    location: str | list[str] = ["database", "collection"],
    driver_path: str | list[str] = "/usr/bin/geckodriver",
) -> IODD:
    """Scrape the IODD finder for the desired sensor IODD file.

    ***Important***: This currently relies on Firefox being installed -> should be
    noted somehow or checked in the function!

    :param sensors: Name of your sensor(s)
    :param location: Relative location of the IODD collection,
    defaults to "database/collection"
    :param driver_path: Path to the Firefox driver,
    defaults to "/usr/bin/geckodriver" -> for Docker container
    """
    _logger = logging.getLogger("IODDCollection")
    cwd = os.getcwd()

    if isinstance(location, list):
        location = os.path.normpath(os.path.join(*location))

    if not os.path.exists(os.path.normpath(os.path.join(cwd, ".tmp"))):
        _logger.info("Creating temporary directory to store downloaded files")
        os.mkdir(os.path.normpath(os.path.join(cwd, ".tmp")))
    elif os.listdir(os.path.normpath(os.path.join(cwd, ".tmp"))) != []:
        _logger.info(
            "The temporary directory existed and has content in it that will be removed"
        )
        for f in os.listdir(os.path.normpath(os.path.join(cwd, ".tmp"))):
            os.remove(os.path.normpath(os.path.join(cwd, ".tmp", f)))

    # Configuring the browser used with Selenium
    browser_options = Options()
    browser_options.headless = True
    browser_options.set_preference("browser.download.folderList", 2)
    browser_options.set_preference("browser.download.manager.showWhenStarting", False)
    browser_options.set_preference(
        "browser.download.dir", os.path.normpath(os.path.join(cwd, ".tmp"))
    )
    browser_options.set_preference(
        "browser.helperApps.neverAsk.saveToDisk", "application/x-gzip"
    )

    terms_accepted = False
    driver = webdriver.Firefox(
        service=Service(executable_path=driver_path),
        options=browser_options,
    )
    driver.implicitly_wait(5)

    # Scraping IODDfinder for the sensors IODD
    driver.get(
        "https://ioddfinder.io-link.com/productvariants/"
        f"search?productName=%22{sensor}%22"
    )

    # If the IODD is not available in IODDfinder, a text will be displayed instead
    # of the table -> Try find that text to see if the sensor was found
    try:
        driver.find_element(by=By.XPATH, value="//*[./text()='No data to display']")
        os.rmdir(os.path.normpath(os.path.join(cwd, ".tmp")))
        raise IODDNotFoundError(sensor)
    except NoSuchElementException:
        pass

    # If the IODD was found in IODDfinder, download it and process it
    download_button = driver.find_element(by=By.XPATH, value="//datatable-body-cell")
    _logger.debug(f'{sensor}:Found "Download" button')
    download_button.click()
    if not terms_accepted:
        try:
            accept_button = driver.find_element(
                by=By.XPATH, value="//*[./text()='Accept']"
            )
        except NoSuchElementException:
            try:
                accept_button = driver.find_element(
                    by=By.XPATH, value="//*[./text()='Akzeptieren']"
                )
            except NoSuchElementException as e:
                _logger.warning('Could not find "Accept" button')
                raise e
        _logger.debug('Found "Accept" button')
        accept_button.click()
        terms_accepted = True
    while not os.path.exists(os.path.normpath(os.path.join(cwd, ".tmp", "iodd.zip"))):
        _logger.debug(f"{sensor}:Waiting for download to finish...")
        time.sleep(1)
    _logger.debug(f"{sensor}:Download finished")

    # Handling downloaded zip file
    with ZipFile(os.path.normpath(os.path.join(cwd, ".tmp", "iodd.zip"))) as archive:
        file_found = False
        for info in archive.infolist():
            if re.search("(IODD1.1.xml)", info.filename):
                _logger.debug(f"{sensor}:Found IODD file in zip archive")
                file_found = True
                if os.path.exists(
                    os.path.normpath(os.path.join(location, info.filename))
                ):
                    _logger.info(
                        f"{sensor}:IODD file already exists and will " "be replaced"
                    )
                    os.remove(os.path.normpath(os.path.join(location, info.filename)))
                archive.extract(member=info.filename, path=location)
                path_to_file = os.path.normpath(
                    os.path.join(cwd, location, info.filename)
                )
                break
        if not file_found:
            os.rmdir(os.path.normpath(os.path.join(cwd, ".tmp")))
            raise IODDNotFoundError(sensor)
    # Remove the zip file to avoid multiple files with hard to track names, e.g.
    # IODD (1).zip etc.
    os.remove(os.path.normpath(os.path.join(cwd, ".tmp", "iodd.zip")))

    os.rmdir(os.path.normpath(os.path.join(cwd, ".tmp")))
    driver.quit()
    return IODD(path_to_file)


def update_from_collection_folder(
    conn: sqlite3.Connection, cur: sqlite3.Cursor
) -> None:
    """Update the IODDCollection based on the files in the collection folder.

    :param conn: Connection object that points to database which houses the collection
    :param cur: Cursor object used for executing queries
    """
    ioddcollection = IODDCollection()
    save(conn=conn, cur=cur, collection=ioddcollection)


def validate_index(conn: sqlite3.Connection, cur: sqlite3.Cursor) -> None:
    """Validate the index.

    If the IODD file of an entry in the index doesn't exist in the collection,
    it will be deleted from the index.

    :param conn: Connection object that points to database which houses the collection
    :param cur: Cursor object used for executing queries
    """
    _logger = logging.getLogger("IODDCollection")
    rows = cur.execute("select * from ioddcollection")
    for row in rows.fetchall():
        if not os.path.exists(row[1]):
            _logger.info(
                f"IODD for sensors {row[0]} missing from collection. Index entry "
                "will be removed"
            )
            cur.execute(f"delete from ioddcollection where file_loc == {row[1]}")
    conn.commit()
    _logger.debug("IODD collection index validated")
