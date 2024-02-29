from enum import Enum

class FileType(Enum):
    """
    Enum for different acceptable file types
    """
    CSV = 1
    PDF = 2
    EXCEL = 3
    DOC = 4
    DOCX = 5
    PPT = 6
    PPTX = 7
    PNG = 8
    JPG = 9
    TIFF = 10
    TXT = 11
    RTF = 12
    XLS = 13
    XLSX = 14
    UNKNOWN = 15
    MSG = 16
    EML = 17