from typing import List

from indico.types.base import BaseType
from indico.types.datafile import Datafile

class DataColumn(BaseType):
    id: int
    name: str

class LabelSet(BaseType):
    id: int 
    name: str

class Dataset(BaseType):
    id: int
    name: str   
    rowCount: int
    status: str
    permissions: str
    files: List[Datafile]
    labelsets: List[LabelSet]
    datacolumns: List[DataColumn]

    def labelset_by_name(self, name: str) -> LabelSet:
        return next(l for l in self.labelsets if l.name == name)

    def datacolumn_by_name(self, name: str) -> DataColumn:
        return next(l for l in self.datacolumns if l.name == name)