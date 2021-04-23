from indico.types.base import BaseType
from typing import List
import datetime


class UserPermissionsReport(BaseType):
    date: datetime
    user: str
    dataset: str


class AppRoles(BaseType):
    role: str
    count: int


class UserDatasets(BaseType):
    dataset_id: int
    role: str


class UserSummaryUser(BaseType):
    enabled: int
    disabled: int


class UserSnapshot(BaseType):
    id: int
    name: str
    email: str
    created_at: str
    enabled: bool
    roles: List[str]
    datasets: List[UserDatasets]


class UserSnapshots(BaseType):
    results: List[UserSnapshot]


class UserMetricsFilters(BaseType):
    date: str
    user_id: str
    user_email: str

    def __init__(self, **kwargs):
        self.date = kwargs.get('date', None).strftime('%Y-%m-%d') if kwargs.get('date', None) is not None else ""
        self.user_id = kwargs.get('user_id', "")
        self.user_email = kwargs.get('user_email', "")

    def to_json(self):
        return {'date': self.date,
                'userId': self.user_id,
                'userEmail': self.user_email}


class UserSummary(BaseType):
    users: UserSummaryUser
    app_roles: List[AppRoles]
