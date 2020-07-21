Workflows
*********

Introduction
============

The Indico Platform includes the ability to link models and operations together into Workflows. Here's a
visual example from one of the Platform's demo workflows.

.. image:: sample-workflow.png

In this case, we are linking document OCR to a classification model and the output of the classifiction model 
to an extraction model - a very common use case for workflows. The input to the workflow is paragraphs from 10K/10Q 
SEC filings. Each paragraph is passed through the classifiction model. If a paragraph is classified as a 
Material Change then it's next passed through a second model to extract individual fields.

Know that Workflows can only be created in the Indico Application. However, you can pass samples through a Workflow
either in the app using "TEST WORKFLOW" or via API.


Running Workflows via API
=========================

The following snippet shows the crux of how to run a sample through a Workflow::

    # Send a document through the workflow
    job = client.call(
        WorkflowSubmission(files=["./path/to/sample.pdf"], workflow_id=workflows[0].id)
    )

    # Retrieve and print your result
    status = client.call(JobStatus(id=job.id, wait=True))
    wf_result = client.call(RetrieveStorageObject(status.result))
    print(wf_result)

In the above snippet, we passed a PDF file through the Workflow but you could also choose
to pass TIF, PNG or JPG image files.  The returned result is Comma Separated Values (CSV)
that detail each step of the workflow results.

See the :doc:`examples` section for a full Workflows example.