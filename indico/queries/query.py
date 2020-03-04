from typing import Dict, Any, Union, List

class BaseQuery:
    query: str = None
    variables: Dict[str, Any] = None

    def __init__(self, query: str, variables: Dict[str, any]):
        self.variables = variables
        self.query = query

    def build_result(self, result: Union[List[Dict[str, Any]], Dict[str, Any]]) -> Union[List[Dict[str, Any]], Dict[str, Any]]:
        return result
