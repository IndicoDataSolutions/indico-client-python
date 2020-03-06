# DATASET QUERIES
DATASET_UPLOAD_STATUS = "query getSharknadoNewDataset($id: Int!) {\n  dataset(id: $id) {\n    id\n    status\n    files {\n      id\n      name\n      deleted\n      fileSize\n      rainbowUrl\n      fileType\n      fileHash\n      status\n      statusMeta\n      __typename\n    }\n    __typename\n  }\n}\n"
DATASET_STATUS = "query datasetStatus($id: Int!) {dataset(id: $id) {status}}"
CREATE_DATASET_MUTATION = "mutation createSharknadoDataset($metadata: JSONString!) {\n  newDataset(metadataList: $metadata) {\n    id\n    status\n    __typename\n  }\n}\n"
FINISH_DATASET_PIPELINE = "mutation processSharknadoDataset($datasetId: Int!, $name: String, $ocr: Boolean) {\n  processDataset(datasetId: $datasetId, ocr: $ocr, name: $name) {\n    id\n    status\n    __typename\n  }\n}\n"

# MODEL GROUP QUERIES
CREATE_MODEL_GROUP = "mutation createMoonbowModelGroup($datasetId: Int!, $interlabelerResolution: LabelResolutionStrategy, $sourceColumnId: Int!, $labelsetColumnId: Int, $name: String!, $processors: [InputProcessor]) {\n  createModelGroup(datasetId: $datasetId, interlabelerResolution: $interlabelerResolution, sourceColumnId: $sourceColumnId, labelsetColumnId: $labelsetColumnId, name: $name, processors: $processors) {\n    id\n    __typename\n  }\n}\n"

