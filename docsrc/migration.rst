********************************
Migrating Client Library Scripts
********************************

V3.1 of the Indico Client Library is a complete departure from older versions. Below is a list
of old vs new operations that should help you migrate scripts to use V3.1+. In general, know that
V3.1+ of the new Client Library is **much** more flexible than the old version and requires a
few more lines of code.


Authentication & Initialization
===============================

Old::

    import indicoio

    indicoio.config.api_key = "my api key"
    indicoio.config.host = "indico.mycompany.com"


New::

    from indico.client import IndicoClient, IndicoConfig

    my_config = IndicoConfig(
        host='indico.mycompany.com',
        api_token_path='/home/myuser/projects/trades/indico_api_token.txt'
    )

    client = IndicoClient(config=my_config)


Optical Character Recognition (OCR)
===================================

Old::

    json_result = indicoio.pdf_extraction(
        ['./path_to_file.pdf'],
        version=2,
        single_column=False,
        text=False,
        metadata=False,
        raw_text=True
        tables=False,
        job_options={"job": True})

New::

    from indico.queries import JobStatus, RetrieveStorageObject, DocumentExtraction

    jobs = client.call(DocumentExtraction(files=['./path_to_file.pdf']))
    job = client.call(JobStatus(id=jobs[0].id, wait=True))
    json_result = client.call(RetrieveStorageObject(job.result))

The new DocumentExtraction class has many more configurable options. Be sure to consult the
:doc:`docextract_settings` page and find the best combination of setting to match your use case.


Getting Model Predictions
=========================

Old::

    texts = ['document text...', 'document text...']
    model = Collection('4137_23703_1582037135')
    all_preds = model.predict(texts)

New::
    
    from indico.queries import ModelGroupPredict, JobStatus
    
    job = client.call(
        ModelGroupPredict(
            model_id=921, # derived from ModelGroup.selected_model.id
            data=['a text sample'],
            )
        )
    prediction = client.call(
        JobStatus(id=job.id, wait=True)
        ).result


Collections have been replaced with Model Groups in the Indico Client Library. Instead of passing
a collection name to create a model, you would now pass in the model group id. For predictions, you
also pass in the model group's selected model id. See the :doc:`concepts` page For details.

Also, with prior versions of the Client Library, you had to be careful to distinguish between a
``Collection`` and a ``FinetuneCollection``. This is no longer the case. ModelGroups will handle
this for you automatically.


Training Models
===============

Old::

    import indicoio
    from indicoio.custom import Collection

    collection = Collection('financial_statements', domain='standard')
    collection.add_data(labeled_samples)
    res = collection.train()
    collection.wait()

New::


    from indico.types import Dataset, ModelGroup
    from indico.queries import CreateDataset, CreateModelGroup


    dataset = client.call(
            CreateDataset(name="financial_documents", files=['./financial_docs.csv'])
        )
    
    mg = client.call(
        CreateModelGroup(
            name='my_classification_model',
            dataset_id=dataset.id,
            source_column_id=dataset.datacolumn_by_name('text').id,
            labelset_id=dataset.labelset_by_name('target_class').id,
            wait=True # wait for training to finish
            )
        )
