from indico.types.base import BaseType

class Datafile(BaseType):
    id: int
    name: str
    deleted: bool
    fileSize: int
    rainbowUrl: str
    fileType: str
    fileHash: str
    status: str
    statusMeta: str

