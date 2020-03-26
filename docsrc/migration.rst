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
    indicoio.config.host = "indico.myco.com"


New::

    from indico import IndicoClient
    from indico.config import IndicoConfig

    my_config = IndicoConfig(
        host='app.mycompany.com',
        api_token_path='/home/myuser/projects/trades/indico_api_token.txt'
    )

    client = IndicoClient(config=my_config)


Optical Character Recognition (OCR)
===================================

Old::

    json_result = indicoio.pdf_extraction(
        src_path,
        version=2,
        single_column=False,
        text=False,
        metadata=False,
        raw_text=True
        tables=False,
        job_options={"job": True})

New::
    from indico import IndicoClient
    from indico.config import IndicoConfig
    from indico.queries.documents import DocumentExtraction
    from indico.queries.jobs import JobStatus

    job = client.call(DocumentExtraction(files=[src_path], json_config='{"preset_config": "legacy"}'))
    job = client.call(JobStatus(id=job[0].id, wait=True))

The new DocumentExtraction class has many more configurable options. Be sure to consult the
:doc:`docextract_settings` page and find the best combination of setting to match your use case.


Getting Model Predictions
=========================

Old::

    texts = []

    # ... samples are appended to texts

    model = Collection("4137_23703_1582037135")
    all_preds = model.predict(texts)

New::

    def predict(client: IndicoClient, model_group: ModelGroup, data: List[str]):
        job = client.call(ModelGroupPredict(
            model_id=model_group.selected_model.id,
            data=data
        ))

        return client.call(JobStatus(id=job.id, wait=True)).result

    #... later in your script, call predict
    predict(client, mg, ["I need wifi"])

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

    import os
    import time
    from pathlib import Path
    from typing import List


    from indico import IndicoClient
    from indico.config import IndicoConfig
    from indico.types import Dataset, ModelGroup
    from indico.queries import (
        CreateDataset,
        GetDatasetStatus,
        CreateModelGroup,
        JobStatus)


    def create_dataset(client) -> Dataset:
        dataset_filepath = "./airline-comments.csv"
        response = client.call(CreateDataset(name=f"AirlineComplaints-test-{int(time.time())}", files=[dataset_filepath]))
        return response

    def create_model_group(client, dataset) -> ModelGroup:
        mg: ModelGroup = client.call(CreateModelGroup(
            name=f"TestCreateModelGroup-{int(time.time())}",
            dataset_id=dataset.id,
            source_column_id=dataset.datacolumn_by_name("Text").id,
            labelset_id=dataset.labelset_by_name("Target_1").id,
            wait=True   # Waits for model group to finish training
        ))
        return mg

    if __name__ == "__main__":
        os.chdir(Path(__file__).parent)

        config = IndicoConfig(host='indico.myco.com')
        client = IndicoClient(config=config)

        dataset = create_dataset(client)
        status = client.call(GetDatasetStatus(dataset.id))
        print(f"Dataset status: {status}")

        mg = create_model_group(client, dataset)