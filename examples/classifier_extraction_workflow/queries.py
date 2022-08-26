from config import INDICO_CLIENT
from indico.queries import GraphQLRequest


def get_user_ids(dataset_id):
    get_user_id_query = """
    query getDatasetUsers($datasetId: Int) {
        dataset(id: $datasetId) {
            users {
            email
            role
            userId

            }
        }
    }
    """
    variables = {"datasetId": dataset_id}
    resp = INDICO_CLIENT.call(GraphQLRequest(get_user_id_query, variables))
    user_ids = [user["userId"] for user in resp["dataset"]["users"]]
    return user_ids


def get_component_links(workflow_id):
    workflow_query = """
        query ListWorkflows($workflowIds: [Int]){
            workflows(workflowIds: $workflowIds){
                workflows {                   
                    componentLinks{
                        id
                        headComponentId
                        tailComponentId
                        filters{
                            classes
                        }                        
                    }
                }
            }
        }            
    """
    variables = {"workflowIds": [workflow_id]}
    resp = INDICO_CLIENT.call(GraphQLRequest(workflow_query, variables))
    return resp["workflows"]["workflows"][0]["componentLinks"]
