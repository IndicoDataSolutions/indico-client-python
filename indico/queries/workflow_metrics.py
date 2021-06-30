from datetime import datetime
from indico.errors import IndicoInputError
from indico.client.request import GraphQLRequest
<<<<<<< HEAD
<<<<<<< HEAD
from indico.types import BaseType
from indico.types.workflow_metrics import WorkflowMetricsOptions, WorkflowMetrics
from typing import List


class _WorkflowMetric(BaseType):
    metrics: WorkflowMetrics


class _TopWorkflowMetric(BaseType):
    workflows: List[_WorkflowMetric]


class GetWorkflowMetrics(GraphQLRequest):
    """
    Requests detailed workflow metric data.
    Includes daily and total submission counts,
    Review queue counts, and Straight through processing details.
    Query can be configured to include only specific metrics
    by passing in one of WorkflowOptions for SUBMISSIONS,
    REVIEW, or STRAIGHT_THROUGH_PROCESSING.

    Args:
        options (List[WorkflowMetricsOptions]): specific metrics to return.
        start_date (datetime): start date for metrics data.
        end_date (datetime): end date for metrics data. defaults to today.
        workflow_ids (List[int]): ids of specific workflows to query.

    """
    __MAP_WORKFLOW_KEYS = {
        WorkflowMetricsOptions.SUBMISSIONS: """
        firstSubmittedDate
               submissions {               
                  aggregate {
                    submitted
                    completed
                    completedInReview
                    completedReviewQueue
                    completedExceptionQueue
                    rejectedInReview
                  }
                  daily {
                    date
                    submitted
                    completed
                    completedInReview
                    completedReviewQueue
                    completedExceptionQueue
                    rejectedInReview
                  }
               }""",
        WorkflowMetricsOptions.REVIEW: """ queues {
                  dailyCumulative {
                    date
                    subsOnQueue
                    hoursOnQueue
                    avgAgeInQueue # (num_hours / num_subs )
                  }
               }
               """,
        WorkflowMetricsOptions.STRAIGHT_THROUGH_PROCESSING: """
              straightThroughProcessing {
                workflow {
                  daily {
                    date
                    reviewNumerator
                    autoReviewNumerator
                    reviewDenom
                    autoReviewDenom
                    reviewStpPct
                    autoReviewStpPct
                  }
                }
                model {
                  modelGroupId
                  name
                  aggregate {
                    reviewNumerator
                    autoReviewNumerator
                    reviewDenom
                    autoReviewDenom
                    reviewStpPct
                    autoReviewStpPct
                  }
                  daily {
                    date
                    reviewNumerator
                    autoReviewNumerator
                    reviewDenom
                    autoReviewDenom
                    reviewStpPct
                    autoReviewStpPct
                  }
                  classMetrics {
                    className
                    aggregate {
                      reviewNumerator
                      autoReviewNumerator
                      reviewDenom
                      autoReviewDenom
                      reviewStpPct
                      autoReviewStpPct                    
                    }
                    daily {
                      date
                      reviewNumerator
                      autoReviewNumerator
                      reviewDenom
                      autoReviewDenom
                      reviewStpPct
                      autoReviewStpPct
                    }
                  }
                }
            }
                """,
        WorkflowMetricsOptions.TIME_ON_TASK: """
               timeOnTask {
                  aggregate { 
                    avgMinsPerDoc
                    avgMinsPerDocReview
                    avgMinsPerDocExceptions
                  }
                  daily {
                    date
                    avgMinsPerDoc
                    avgMinsPerDocReview
                    avgMinsPerDocExceptions
                  }
               }
        """

    }
    query = """
query ($workflowIds: [Int]!, $startDate: Date, $endDate:Date) {
    workflows(workflowIds: $workflowIds){
        workflows {
            metrics(startDate:$startDate, endDate:$endDate){
               firstSubmittedDate
               workflowId
               __QUERY_OPTS__
              }
            }
        }
}
"""

    def __init__(self, options: List[WorkflowMetricsOptions], start_date: datetime, end_date: datetime,
                 workflow_ids: List[int]):
        self.query = self.__map_query_values(options)
        if workflow_ids is None or start_date is None:
            raise IndicoInputError("Must specify date and workflow id")
        if end_date is None:
            end_date = datetime.now()
        super().__init__(self.query, variables={"startDate": start_date.strftime('%Y-%m-%d'),
                                                "endDate": end_date.strftime('%Y-%m-%d'), "workflowIds": workflow_ids})

    def process_response(self, response) -> List[WorkflowMetrics]:
        list_of_metrics = _TopWorkflowMetric(**super().process_response(response)["workflows"]).workflows
        return list(map(lambda x: x.metrics, list_of_metrics))

    def __map_query_values(self, options: List[WorkflowMetricsOptions]):
        daily = ' '
        if len(options) < 1:
            daily = ' '.join([self.__MAP_WORKFLOW_KEYS[a] for a in self.__MAP_WORKFLOW_KEYS.keys()])
        else:
            daily = ' '.join([self.__MAP_WORKFLOW_KEYS[a] for a in options])
        query = self.query.replace("__QUERY_OPTS__", daily)
        return query
=======
from indico.types import workflow_metrics
from indico.types.workflow import Workflow
from indico.types.workflow_metrics import WorkflowMetrics, WorkflowMetricsOptions
from typing import List
=======
>>>>>>> workflow metrics changes
from indico.types import BaseType
from indico.types.workflow_metrics import WorkflowMetricsOptions, WorkflowMetrics
from typing import List
import itertools


class _WorkflowMetric(BaseType):
    metrics: WorkflowMetrics


class _TopWorkflowMetric(BaseType):
    workflows: List[_WorkflowMetric]


class GetWorkflowMetrics(GraphQLRequest):
    """
    Requests detailed workflow metric data.
    Includes daily and total submission counts,
    Review queue counts, and Straight through processing details.
    Query can be configured to include only specific metrics
    by passing in one of WorkflowOptions for SUBMISSIONS,
    REVIEW, or STRAIGHT_THROUGH_PROCESSING.

    Args:
        options (List[WorkflowMetricsOptions]): specific metrics to return.
        start_date (datetime): start date for metrics data.
        end_date (datetime): end date for metrics data. defaults to today.
        workflow_ids (List[int]): ids of specific workflows to query.

    """
    __MAP_WORKFLOW_KEYS = {
        WorkflowMetricsOptions.SUBMISSIONS: """
        firstSubmittedDate
               submissions {               
                  aggregate {
                    submitted
                    completed
                    completedInReview
                    completedReviewQueue
                    completedExceptionQueue
                    rejectedInReview
                  }
                  daily {
                    date
                    submitted
                    completed
                    completedInReview
                    completedReviewQueue
                    completedExceptionQueue
                    rejectedInReview
                  }
               }""",
        WorkflowMetricsOptions.REVIEW: """ queues {
                  dailyCumulative {
                    date
                    subsOnQueue
                    hoursOnQueue
                    avgAgeInQueue # (num_hours / num_subs )
                  }
               }
               timeOnTask {
                  aggregate { 
                    avgMinsPerDoc
                    avgMinsPerDocReview
                    avgMinsPerDocExceptions
                  }
                  daily {
                    date
                    avgMinsPerDoc
                    avgMinsPerDocReview
                    avgMinsPerDocExceptions
                  }
               }
               """,
        WorkflowMetricsOptions.STRAIGHT_THROUGH_PROCESSING: """
              straightThroughProcessing {
                workflow {
                  daily {
                    date
                    reviewNumerator
                    autoReviewNumerator
                    reviewDenom
                    autoReviewDenom
                    reviewStpPct
                    autoReviewStpPct
                  }
                }
                model {
                  modelGroupId
                  name
                  aggregate {
                    reviewNumerator
                    autoReviewNumerator
                    reviewDenom
                    autoReviewDenom
                    reviewStpPct
                    autoReviewStpPct
                  }
                  daily {
                    date
                    reviewNumerator
                    autoReviewNumerator
                    reviewDenom
                    autoReviewDenom
                    reviewStpPct
                    autoReviewStpPct
                  }
                  classMetrics {
                    className
                    aggregate {
                      reviewNumerator
                      autoReviewNumerator
                      reviewDenom
                      autoReviewDenom
                      reviewStpPct
                      autoReviewStpPct                    
                    }
                    daily {
                      date
                      reviewNumerator
                      autoReviewNumerator
                      reviewDenom
                      autoReviewDenom
                      reviewStpPct
                      autoReviewStpPct
                    }
                  }
                }
            }
                """

    }
    query = """
query ($workflowIds: [Int]!, $startDate: Date, $endDate:Date) {
    workflows(workflowIds: $workflowIds){
        workflows {
            metrics(startDate:$startDate, endDate:$endDate){
               firstSubmittedDate
               workflowId
               __QUERY_OPTS__
              }
            }
        }
}
"""

    def __init__(self, options: List[WorkflowMetricsOptions], start_date: datetime, end_date: datetime,
                 workflow_ids: List[int]):
        self.query = self.__map_query_values(options)
        if workflow_ids is None or start_date is None:
            raise IndicoInputError("Must specify date and workflow id")
        if end_date is None:
            end_date = datetime.now()
        super().__init__(self.query, variables={"startDate": start_date.strftime('%Y-%m-%d'),
                                                "endDate": end_date.strftime('%Y-%m-%d'), "workflowIds": workflow_ids})

    def process_response(self, response) -> List[WorkflowMetrics]:
        list_of_metrics = _TopWorkflowMetric(**super().process_response(response)["workflows"]).workflows
        return list(map(lambda x: x.metrics, list_of_metrics))

    def __map_query_values(self, options: List[WorkflowMetricsOptions]):
        daily = ' '
        if len(options) < 1:
<<<<<<< HEAD
            return ''
        strs = [self.__MAP_WORKFLOW_KEYS[a] for a in options]
        opts = ' '.join(strs)
        return opts
>>>>>>> items submitted
=======
            daily = ' '.join([self.__MAP_WORKFLOW_KEYS[a] for a in self.__MAP_WORKFLOW_KEYS.keys()])
        else:
            daily = ' '.join([self.__MAP_WORKFLOW_KEYS[a] for a in options])
        query = self.query.replace("__QUERY_OPTS__", daily)
        return query
>>>>>>> workflow metrics changes
