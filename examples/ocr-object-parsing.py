"""
Example demonstrating how to OCR a document and access the text at the document, page, and 
block (or paragraph) level.
"""

from indico import IndicoClient, IndicoConfig
from indico.queries import DocumentExtraction, JobStatus, RetrieveStorageObject

# Get the OCR object
my_config = IndicoConfig(
    host="app.indico.io", api_token_path=".path/to/indico_api_token.txt"
)
client = IndicoClient(config=my_config)

files_to_extract = client.call(
    DocumentExtraction(
        files=['./test_paragraphs.pdf'], 
        json_config={'preset_config': 'standard'}
    )
)
extracted_file = client.call(JobStatus(id=files_to_extract[0].id, wait=True))
json_result = client.call(RetrieveStorageObject(extracted_file.result))

# The code below shows how to get the OCR text from the 'json_result' object. 
# Note: it may vary slightly if you use DocumentExtraction configurations other than 'standard'

# Full Text
full_document_text = json_result['text'] 

# Doucment Text split by page
text_by_page = list()
for page in json_result['pages']:
    text_by_page.append(page['text'])

# Document Text split by block (or paragraph)
text_by_block = list()
for page in json_result['pages']:
    for block in page['blocks']:
        text_by_block.append(block['text'])