from typing import List

from indico.types.base import BaseType
from indico.types.datafile import Datafile

class Dataset(BaseType):
    id: int
    name: str   
    rowCount: int
    status: str
    permissions: str
    files: List[Datafile]

