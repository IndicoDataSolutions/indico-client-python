from datetime import datetime
from typing import TYPE_CHECKING

from indico.client.request import GraphQLRequest
from indico.errors import IndicoInputError
from indico.types import BaseType
from indico.types.workflow_metrics import WorkflowMetrics, WorkflowMetricsOptions

if TYPE_CHECKING:  # pragma: no cover
    from typing import List

    from indico.typing import Payload


class _WorkflowMetric(BaseType):
    metrics: WorkflowMetrics


class _TopWorkflowMetric(BaseType):
    workflows: List[_WorkflowMetric]


class GetWorkflowMetrics(GraphQLRequest["List[WorkflowMetrics]"]):
    """
    Requests detailed workflow metric data, including daily and total submission counts, review queue counts, and straight through processing details.
    Query can be configured to include only specific metrics by passing in one of WorkflowOptions for SUBMISSIONS, REVIEW, or STRAIGHT_THROUGH_PROCESSING.

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
        """,
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

    def __init__(
        self,
        options: "List[WorkflowMetricsOptions]",
        start_date: datetime,
        end_date: datetime,
        workflow_ids: "List[int]",
    ):
        self.query = self.__map_query_values(options)
        if workflow_ids is None or start_date is None:
            raise IndicoInputError("Must specify date and workflow id")
        if end_date is None:
            end_date = datetime.now()

        super().__init__(
            self.query,
            variables={
                "startDate": start_date.strftime("%Y-%m-%d"),
                "endDate": end_date.strftime("%Y-%m-%d"),
                "workflowIds": workflow_ids,
            },
        )

    def __map_query_values(self, options: "List[WorkflowMetricsOptions]") -> str:
        daily = " "
        if len(options) < 1:
            daily = " ".join(
                [self.__MAP_WORKFLOW_KEYS[a] for a in self.__MAP_WORKFLOW_KEYS.keys()]
            )
        else:
            daily = " ".join([self.__MAP_WORKFLOW_KEYS[a] for a in options])

        query: str = self.query.replace("__QUERY_OPTS__", daily)
        return query

    def process_response(self, response: "Payload") -> "List[WorkflowMetrics]":
        list_of_metrics = _TopWorkflowMetric(
            **super().parse_payload(response)["workflows"]
        ).workflows

        return [x.metrics for x in list_of_metrics]
