from indico import IndicoClient, IndicoConfig

HOST = "indico.host"
API_TOKEN_PATH = "/path/to/indico_api_token.txt"

INDICO_CONFIG = IndicoConfig(host=HOST, api_token_path=API_TOKEN_PATH)
INDICO_CLIENT = IndicoClient(config=INDICO_CONFIG)
DATASET_ID = 11564

CLASSIFIER_CLASSES = ["class A", "class B"]