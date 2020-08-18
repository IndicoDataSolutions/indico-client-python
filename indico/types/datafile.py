from indico.types.base import BaseType


class Datafile(BaseType):
    """
    A Datafile in the Indico Platform.

    Datafiles are primarlily used in retrieving stored results.

    Attributes:
        id (int): The Datafile id
        name (str): Datafile name
        deleted (bool): Has the datafile been marked for deletion
        rainbow_url (str): URL of the datafile within the Indico Platform
        file_type (str): Filetype of the datafile
        file_hash (str): Location of the datafile
        status (str): Processing status of the datafile
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
    failure_type: str
