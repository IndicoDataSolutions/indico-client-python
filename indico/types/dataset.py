from enum import Enum
from typing import List, Optional

from indico.errors import IndicoInputError
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
        row_count (int): Number of rows in the dataset
        permissions (str): Permissions on the dataset
        files (List[Datafile]): Names of the file(s) included in the dataset
        labelsets (List[LabelSet]): LabelSets associated with this dataset
        datacolumns (List[DataColumn]): DataColumn(s) of the dataset
    """

    id: int
    name: str
    row_count: int
    status: str
    permissions: str
    files: List[Datafile]
    labelsets: List[LabelSet]
    datacolumns: List[DataColumn]

    def labelset_by_name(self, name: str) -> LabelSet:
        if name not in [lab.name for lab in self.labelsets]:
            raise IndicoInputError(
                f"No labelset found for {name}. Current labelset names include {[lab.name for lab in self.labelsets]}."
            )
        return next(lab for lab in self.labelsets if lab.name == name)

    def datacolumn_by_name(self, name: str) -> DataColumn:
        if name not in [datacol.name for datacol in self.datacolumns]:
            raise IndicoInputError(
                f"No datacolumn found for {name}. Current datacolumn names include {[datacol.name for datacol in self.datacolumns]}."
            )
        return next(datacol for datacol in self.datacolumns if datacol.name == name)


class TableReadOrder(Enum):
    ROW = 0
    COLUMN = 1


class OcrEngine(Enum):
    """
    Enum representing available OCR engines.
    """

    OMNIPAGE = 0
    READAPI = 1
    READAPI_V2 = 2
    READAPI_TABLES_V1 = 3


class OmnipageOcrOptionsInput(BaseType):
    """
    Omnipage specific OCR options for dataset creation.

    Args:
        auto_rotate(bool): auto rotate.
        single_colum(bool): Read table as a single column.
        upscale_images(bool): Scale up low-resolution images.
        languages(List[OmnipageLanguageCode]): List of languages to use in ocr.
        cells(bool): Return table information for post-processing rules
        force_render(bool): Force rednering.
        native_layout(bool): Native layout.
        native_pdf(bool): Native pdf.
        table_read_order(TableReadOrder): Read table by row or column.

    """

    auto_rotate: bool
    single_column: bool
    upscale_images: bool
    languages: List[str]
    cells: bool
    force_render: bool
    native_layout: bool
    native_pdf: bool
    table_read_order: TableReadOrder


class ReadApiOcrOptionsInput(BaseType):
    """
    Read API OCR options.

    Args:
        auto_rotate(bool): Auto rotate
        single_column(bool): Read table as a single column.
        upscale_images(bool): Scale up low resolution images.
        languages(List[str]): List of languages to use.
    """

    auto_rotate: bool
    single_column: bool
    upscale_images: bool
    languages: List[str]


class OcrInputLanguage(BaseType):
    name: str
    code: str


class IncludeSections(BaseType):
    header: Optional[bool]
    body: Optional[bool]
    attachments: Optional[bool]


class EmailOptions(BaseType):
    include_sections: Optional[IncludeSections]
    unpack: Optional[bool]
    preserve_body_whitespace: Optional[bool]


class OcrOptionsInput:
    """
    Input options for OCR engine.
    """

    ocr_engine: OcrEngine
    omnipage_options: OmnipageOcrOptionsInput
    readapi_options: ReadApiOcrOptionsInput
