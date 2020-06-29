Intro to OCR with DocumentExtraction
************************************

The Indico Platform includes a sophisticated OCR engine that's capable of extracting raw
text from a variety of document formats including PDF and TIF. OCR functionality is provided
by the ``DocumentExtraction`` class. Here's how to OCR one document with DocumentExtraction::

    from indico import IndicoClient
    from indico.queries.documents import DocumentExtraction
    from indico.queries import JobStatus, RetrieveStorageObject

    # here, IndicoClient assumes you have your api token in your home directory and host set as an env variable
    client = IndicoClient()
    files_to_extract = client.call(DocumentExtraction(files=['./path_to_document.pdf']))
    extracted_file = client.call(JobStatus(id=files_to_extract[0].id, wait=True))
    result = client.call(RetrieveStorageObject(extracted_file.result))

In this example, given the path to a document, we called DocumentExtraction with a single file and waited for the result.
With most use cases, this is all you will need to do. The returned 'result' will either be a dictionary (if
document-level text and/or metadata are requested) or a list of dictionaries (where each dictionary contains
the text for a unique page/block).

``DocumentExtraction`` is highly configurable. You can customize settings at the document, page, block, token or
character level. You can also choose from a selection of preset configurations. You configure DocumentExtraction
by passing in a Python dictionary or JSON string.

Here's an Example::

    my_ocr_config = {
        "preset_config": "standard"
    }

    job = client.call(DocumentExtraction(files=['./path_to_doc.pdf'], json_config=my_ocr_config))

Visit the :doc:`docextract_settings` page to read the extensive list of DocumentExtraction settings.