import json
import tempfile
from pathlib import Path
from typing import List
import datetime

import pandas as pd
from indico.client.request import (
    Debouncer,
    GraphQLRequest,
    HTTPMethod,
    HTTPRequest,
    RequestChain,
)
from indico.errors import IndicoNotFound
from indico.types.user_metrics import UserSummary, UserSnapshot, UserSnapshots, UserMetricsFilters


class GetUserSummary(GraphQLRequest):
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


class GetUserSnapshots(GraphQLRequest):
    query = """
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

    def __init__(self, **kwargs):

        filters = UserMetricsFilters(**kwargs)

        super().__init__(self.query, variables=filters.to_json())

    def process_response(self, response) -> UserSnapshots:
        return UserSnapshots(**super().process_response(response)["userSnapshot"])
