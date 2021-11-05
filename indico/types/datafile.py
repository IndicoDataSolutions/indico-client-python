from typing import List

from indico.types.base import BaseType


class DataFilePage(BaseType):
    """
    A DataFilePage in the Indico Platform

    DataFilePages give more specific info on individual datafile pages.

    Attributes:
        id (int): The DataFilePage id
        datafile_id (int): The Datafile id associated with this DataFilePage
        image (str): URL to where the image of the file is stored
        page_num (int): The page number of the Datafile associated with this info
        page_info (str): More meta information on the page, such as OCR stats
        thumbnail (str): URL to a smaller, thumbnail version of the DataFilePage image
        doc_start_offset (int): The index position where the page starts
        doc_end_offset (int): The index position where the page ends
    """

    id: int
    datafile_id: int
    image: str
    page_num: int
    page_info: str
    thumb_nail: str
    doc_start_offset: int
    doc_end_offset: int


class Datafile(BaseType):
    """
    A Datafile in the Indico Platform.

    Datafiles are primarlily used in retrieving stored results.

    Attributes:
        id (int): The Datafile id
        deleted (bool): Has the Datafile been marked for deletion
        name (str): Datafile name
        rainbow_url (str): URL of the Datafile within the Indico Platform
        status (str): Processing status of the Datafile
        status_meta (str): Contains metadata about the status of the Datafile, such as errors
        file_hash (str): Location of the Datafile
        file_size (int): Size of the file, in bytes
        file_type (str): Filetype of the Datafile
        page_ids (List[int]): A list of pagge ids associated with the Datafile
        num_pages (int): The number of pages in the Datafile
        pages (List[DataFilePage]): The DatafilePages associated with the Datafile
        failure_type (str): The type of failure associated with the Datafile, if an error was encountered
    """

    id: int
    deleted: bool
    name: str
    rainbow_url: str
    status: str
    status_meta: str
    file_hash: str
    file_size: int
    file_type: str
    page_ids: List[int]
    num_pages: int
    pages: List[DataFilePage]
    failure_type: str
