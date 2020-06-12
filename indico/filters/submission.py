from .base import BaseFilter


class SubmissionFilter(BaseFilter):
    _filterable_columns = {"inputFilename", "status"}
