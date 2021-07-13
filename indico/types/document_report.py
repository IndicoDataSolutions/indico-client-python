"""query SubmissionsLog($filters: SubmissionLogFilter){
  submissionsLog(filters: $filters){
    submissions{
      datasetId
      workflowId
      status
      createdAt
      updatedAt
      updatedBy
      completedAt
      errors
    }
    pageInfo{
      startCursor
      endCursor
      hasNextPage
      aggregateCount
    }
  }
}"""