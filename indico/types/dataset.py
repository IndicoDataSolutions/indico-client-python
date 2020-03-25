from typing import List

from indico.types.base import BaseType
from indico.types.datafile import Datafile


class DataColumn(BaseType):
    """
    A DataColumn in the Indico Platform

    Attributes:
        id (int): The DataColumn id
        name (str): DataColumn name
    """

    id: int
    name: str


class LabelSet(BaseType):
    """
    A LabelSet in the Indico Platform

    Attributes:
        id (int): The LabelSet id
        name (str): LabelSet name
    """

    id: int
    name: str


class Dataset(BaseType):
    """
    A Dataset in the Indico Platform

    Attributes:
        id (int): The Dataset id
        name (str): Dataset name
        rowCount (int): Number of rows in the dataset
        permissions (str): Permissions on the dataset
        files (List[str]): Names of the file(s) included in the dataset
        labelsets (List[LabelSet]): LabelSets associated with this dataset
        datacolumns (List[DataColumn]): DataColumn(s) of the dataset
    """

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