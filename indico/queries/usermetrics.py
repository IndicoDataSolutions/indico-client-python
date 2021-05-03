import datetime
from typing import List, Union, Dict

from indico.client.request import (
    GraphQLRequest,
    PagedRequest,
)
from indico.filters import UserSnapshotFilter
from indico.types import BaseType
from indico.types.user_metrics import UserSummary, UserSnapshot


class _PagedUserSnapshots(BaseType):
    """
    Class to hold paged snapshot data to make parsing easier.
    """
    results: List[UserSnapshot]


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

    def __init__(self, date=None):
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
        filters (UserSnapshotFilter): filter the query based on UserSnapshotFilter criteria.
        date (datetime): specific day to query.
        limit (int): limit how many come back per query or per page.
    """
    query = """
    query GetUserSnapshot($date: Date, $filters: UserReportFilter, $after: Int, $limit: Int){
  userSnapshot(date: $date, filters: $filters, after: $after, limit: $limit){
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

    def __init__(self, *, date: datetime, filters: Union[Dict, UserSnapshotFilter] = None, limit: int = None):
        variables = {
            "date": date.strftime('%Y-%m-%d') if date is not None else None,
            "filters": filters,
            "limit": limit
        }
        super().__init__(self.query, variables=variables)

    def process_response(self, response) -> List[UserSnapshot]:
        return _PagedUserSnapshots(**super().process_response(response)["userSnapshot"]).results
