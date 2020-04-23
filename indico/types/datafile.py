from indico.types.base import BaseType


class Datafile(BaseType):
    """
    A Datafile in the Indico Platform.

    Datafiles are primarlily used in retrieving stored results.

    Attributes:
        id (int): The Datafile id
        name (str): Datafile name
        deleted (bool): Has the datafile been marked for deletion
        rainbowUrl (str): URL of the datafile within the Indico Platform
        fileType (str): Filetype of the datafile
    """

    id: int
    name: str
    deleted: bool
    file_size: int
    rainbow_url: str
    file_type: str
    file_hash: str
    status: str
    status_meta: str
