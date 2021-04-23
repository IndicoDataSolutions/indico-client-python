from typing import List

from indico.client.request import (
    GraphQLRequest,
    PagedRequest,
)
from indico.types import BaseType
from indico.types.user_metrics import UserSummary, UserSnapshot


class _PagedUserSnapshots(BaseType):
    """
    Class to hold paged snapshot data to make parsing easier.
    """
    results: List[UserSnapshot]


class _UserMetricsFilters(BaseType):
    """Filters for fetching user metric data."""
    date: str
    user_id: str
    user_email: str

    def __init__(self, **kwargs):
        self.date = kwargs.get('date', None).strftime('%Y-%m-%d') if kwargs.get('date', None) is not None else ""
        self.user_id = kwargs.get('user_id', "")
        self.user_email = kwargs.get('user_email', "")


class GetUserSummary(GraphQLRequest):
    """
    Requests summary level information per-date of users in the app.
    Includes enabled/disabled user counts, names of roles,
    and number of users assigned to that role.

    Args:
        date (datetime): specific day to summarize.

    """
    query = """
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

    def __init__(self, **kwargs):
        date = kwargs.get('date', None)
        if date is not None:
            super().__init__(self.query, variables={"date": date.strftime('%Y-%m-%d')})
        else:
            super().__init__(self.query)

    def process_response(self, response) -> UserSummary:
        return UserSummary(**super().process_response(response)["userSummary"])


class GetUserSnapshots(PagedRequest):
    """

    Requests per-date detailed information about app users.
    Args:
        user_email (str): the email of a specific user.
        user_id (int): the id of a specific user
        date (datetime): specific day to query
    """
    query = """
    query GetUserSnapshot($date: Date, $filters: UserReportFilter, $after: Int){
  userSnapshot(date: $date, filters: $filters, after: $after){
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

    def __init__(self, **kwargs):
        filters = _UserMetricsFilters(**kwargs)
        variables = {
            'date': filters.date,
            'filters': {
                'userId': filters.user_id,
                'userEmail': filters.user_email
            }
        }
        super().__init__(self.query, variables=variables)

    def process_response(self, response) -> List[UserSnapshot]:
        return _PagedUserSnapshots(**super().process_response(response)["userSnapshot"]).results
