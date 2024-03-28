import datetime
from typing import Dict, List, Union

from indico.client.request import GraphQLRequest, PagedRequest
from indico.filters import UserMetricsFilter
from indico.types import BaseType
from indico.types.user_metrics import (
    UserChangelog,
    UserChangelogReport,
    UserSnapshot,
    UserSummary,
)


class _PagedUserSnapshots(BaseType):
    """
    Class to hold paged snapshot data to make parsing easier.
    """

    results: List[UserSnapshot]


class _PagedUserChangelog(BaseType):
    """
    Class to hold paged snapshot data to make parsing easier.
    """

    results: List[UserChangelog]


class GetUserSummary(GraphQLRequest):
    """
    Requests summary-level information of users in the app on a specific date.

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
            super().__init__(self.query, variables={"date": date.strftime("%Y-%m-%d")})
        else:
            super().__init__(self.query)

    def process_response(self, response) -> UserSummary:
        return UserSummary(**super().process_response(response)["userSummary"])


class GetUserSnapshots(PagedRequest):
    """

    Requests paged detailed information about app users on a specific date.

    Args:
        filters (UserMetricsFilter): filter the query based on UserMetricsFilter criteria.
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

    def __init__(
        self,
        *,
        date: datetime,
        filters: Union[Dict, UserMetricsFilter] = None,
        limit: int = None,
    ):
        variables = {
            "date": date.strftime("%Y-%m-%d") if date is not None else None,
            "filters": filters,
            "limit": limit,
        }
        super().__init__(self.query, variables=variables)

    def process_response(self, response) -> List[UserSnapshot]:
        return _PagedUserSnapshots(
            **super().process_response(response)["userSnapshot"]
        ).results


class GetUserChangelog(PagedRequest):
    """

    Gets paged detailed information about app users.

    Args:
        filters (UserSnapshotFilter): filter the query based on UserMetricsFilter criteria.
        start_date (datetime): specific start date for query.
        end_date (datetime): specific end date for query.
        limit (int): limit how many come back per query or per page.
    """

    query = """
        query GetUserChangelog($sdate: Date, $edate: Date, $filters: UserReportFilter, $after: Int, $limit: Int){
        userChangelog(startDate: $sdate, endDate: $edate, filters: $filters, after:$after, limit:$limit){
            results {
            id
            date
            userEmail
            updaterEmail
            previousDatasets {
                datasetId
                role
            }
            changesMade
        }
        pageInfo{
            aggregateCount
            hasNextPage
            endCursor
        }

        }
    }
        """

    def __init__(
        self,
        *,
        start_date: datetime,
        end_date: datetime,
        filters: Union[Dict, UserMetricsFilter] = None,
        limit: int = None,
    ):
        variables = {
            "sdate": start_date.strftime("%Y-%m-%d")
            if start_date is not None
            else None,
            "edate": end_date.strftime("%Y-%m-%d") if end_date is not None else None,
            "filters": filters,
            "limit": limit,
        }
        super().__init__(self.query, variables=variables)

    def process_response(self, response) -> List[UserSnapshot]:
        return _PagedUserChangelog(
            **super().process_response(response)["userChangelog"]
        ).results


class GenerateChangelogReport(GraphQLRequest):
    """

    Creates a job to generate a report of detailed information about app users

    Args:
        filters (UserSnapshotFilter): filter the query based on UserMetricsFilter criteria.
        start_date (datetime): specific start date for query.
        end_date (datetime): specific end date for query.
        report_format (str): specific format of the report, JSON or CSV.

    """

    query = """
        mutation GenerateChangeReport ($sdate: Date, $edate: Date, $filters: UserReportFilter){
    userChangelogReport(
        startDate: $sdate,
        endDate: $edate,
        filters: $filters,
        reportFormat: JSON
    ){
        jobId
    }
}
        """

    def __init__(
        self,
        *,
        start_date: datetime,
        end_date: datetime,
        filters: Union[Dict, UserMetricsFilter] = None,
        report_format: str = "csv",
    ):
        variables = {
            "sdate": start_date.strftime("%Y-%m-%d")
            if start_date is not None
            else None,
            "edate": end_date.strftime("%Y-%m-%d") if end_date is not None else None,
            "filters": filters,
            "format": report_format,
        }
        super().__init__(self.query, variables=variables)

    def process_response(self, response) -> List[UserSnapshot]:
        return UserChangelogReport(
            **super().process_response(response)["userChangelogReport"]
        )
