from indico.types.base import BaseType
from typing import List
import datetime
import json


def default(self, o):
    if hasattr(o, 'to_json'):
        return o.to_json()
    raise TypeError(f'Object of type {self.__class__.__name__} is not JSON serializable')


"""


query GetUserSnapshot($date: Date, $filters: UserReportFilter){
  userSnapshot(date: $date, filters: $filters){
    results{
      id
      name
      email
      createdAt
      enabled
      roles
      datasets{
        datasetId
        role
      }
      
    }
    pageInfo{
      startCursor
      endCursor
      hasNextPage
      aggregateCount
    }
  }
}
"""


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
    datasets: UserDatasets


class UserSnapshots(BaseType):
    results: List[UserSnapshot]


class UserMetricsFilters(BaseType):
    date: str
    user_id: str
    user_email: str

    def __init__(self, **kwargs):
        self.date = kwargs.get('date', None).strftime('%Y-%m-%d') if kwargs.get('date', None) is not None else ""
        self.user_id = kwargs.get('user_id', None) if kwargs.get("user_id", None) is not None else ""
        self.user_email = kwargs.get('user_email', None) if kwargs.get("user_email", None) is not None else ""

    def to_json(self):
        return {'date': self.date,
                'userId': self.user_id,
                'userEmail': self.user_email}


"""
query GetUserSummary($date: Date){
  userSummary(date: $date){
    users{
      enabled
      disabled
    }
    appRoles {
      role
      count
    }
  }
}
"""

"""
Top level summary of user permission/role data.
"""


class UserSummary(BaseType):
    users: UserSummaryUser
    app_roles: List[AppRoles]
