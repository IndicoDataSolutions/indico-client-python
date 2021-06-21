from datetime import datetime
from indico.errors import IndicoInputError
from indico.client.request import GraphQLRequest
from indico.types import workflow_metrics
from indico.types.workflow import Workflow
from indico.types.workflow_metrics import WorkflowMetrics, WorkflowMetricsOptions
from typing import List
from indico.types import BaseType


class GetWorkflowMetrics(GraphQLRequest):
    __MAP_WORKFLOW_KEYS = {
        WorkflowMetricsOptions.ITEMS_SUBMITTED : 
        """   submitted {
                        date
                        count
                    }
                    submittedAndCompletedInReview {
                        date
                        count
                    }
                    completed {
                        date
                        count
                    }
                    completedInReview {
                        date
                        count
                    }""",
        WorkflowMetricsOptions.ITEMS_THROUGH_REVIEW: 
        """

                    completedReviewQueue {
                        date
                        count
                    }
                    completedExceptionQueue {
                        date
                        count
                    }
                    rejectedInReview {
                        date
                        count
                    }
        """
        
    }
    query = """
    query ($workflowIds: [Int]!, $metricsStartDate: Date) {
    workflows(workflowIds: $workflowIds, metricsStartDate: $metricsStartDate){
        workflows {
            id
            submissionFacts {
                startDate
                workflowId
                total {
                    submitted
                }
                daily {
                    __QUERY_OTPS__
                  }
            }
        }
    }
}
    """

    def __init__(self, options:List[WorkflowMetricsOptions], date: datetime, workflow_id: List[int]):
        opts = self.__map_query_values(options)
        self.query = self.query.replace("__QUERY_OTPS__", opts)
        if workflow_id is None or date is None:
            raise IndicoInputError("Must specify date and workflow id")
        super().__init__(self.query, variables={"date": date.strftime('%Y-%m-%d'), "workflowIds": workflow_id})
    
    def process_response(self, response) -> WorkflowMetrics:
        return WorkflowMetrics(**super().process_response(response)["workflows"])
        

    def __map_query_values(self, options: List[WorkflowMetricsOptions]):
        if len(options) < 1:
            return ''
        strs = [self.__MAP_WORKFLOW_KEYS[a] for a in options]
        opts = ' '.join(strs)
        return opts