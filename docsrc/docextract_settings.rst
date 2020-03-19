OCR With DocumentExtraction
***************************

Introduction
============

The Indico Platform includes a sophisticated OCR engine that's capable of extracting raw
text from a variety of document formats including PDF and TIF. OCR functionality is provided
by the ``DocumentExtraction`` function. Here's how to make a simple call to DocumentExtraction::

    job = client.call(DocumentExtraction(files=[src_path], json_config='{"preset_config": "simple"}'))
    job = client.call(JobStatus(id=job[0].id, wait=True))
    if job is not None and job.status == 'SUCCESS':
        json_data = client.call(RetrieveStorageObject(job.result))
        print(json.dumps(json_data, indent=4))

In this example, we just call DocumentExtraction with a single file and wait for the result.
With most use cases, this is all you will need to do. 

``DocumentExtraction`` is highly configurable. You can choose to customize setting at the
document, page, block, token or character level. You configure DocumentExtraction by passing
in either a Python dictionary or JSON string.

Here's an Example::
    
    my_ocr_config = {
        "preset_config": "simple"
    }

    job = client.call(DocumentExtraction(files=[src_path], json_config=my_ocr_config))


Global Settings
===============

Pre-Set Configurations
----------------------

Setting::

    "preset_config": "simple"
    "preset_config": "legacy"
    "preset_config": "detailed"

Three pre-set ocr configurations are provided: ``legacy``, ``simple`` and ``detailed``. Most users will
only need to use "simple". "legacy" is intended for users who ran Indico's original pdf_extraction
function to extract text and train modes. Use "legacy" if you need to OCR new documents for input
to these models. "detailed" will provide a lot of detail, down to the character level and a 
correspondingly large amount of data.

The exact settings included in "legacy", "simple" and "detailed" are shown at the bottom
of this page.

Result Granularity
------------------

Setting::

    "top_level": "page"
    "top_level": "document"

Choose to have the JSON result returned be either one single result for the entire document or
broken into a list with one item for each page.

Parse Order
-----------

Setting::

    "single_column": True
    "single_column": False

Set to ``True`` to have the document strictly parsed top to bottom as a single column of text.

Table Read Order
----------------

Setting::

    "table_read_order": "row"
    "table_read_order": "column"

Enforce either row or column reading order of tables.

Force Render
------------

Setting::

    "force_render": True
    "force_render": False

Force rendering of document. Beware of increased computation cost for increased reliability of page rendering. 
Only use this setting if you know you’ve got a problem that requires it.

Reblocking
----------

Setting::

    "reblocking": ["style" & "lists"]

Whether we should use a page-level reblocking strategy that can utilize style information, or 
specifically handle list-like documents well or both.

Number of Threads
-----------------

Setting::

    "n_threads": int

How many threads should be used for the portions of the flow that can be multiprocessed? Currently only metadata extraction runs in parallel and defaults to 8 threads, but 
where we find other opportunities for performance improvements they should use this flag.


Document Level Settings
=======================

Page Image
----------

Setting::

    "image": True
    "image": False

Set to ``True`` to retain a full sized image of each page

Page Thumbnails
---------------

Setting::

    "thumbnail":
        "resolution": "<x>x<y>"   # IE - 200x300, defaults to 128x165

Provide this setting to return page thumbnails of the specified resolution. Separate from full
sized images.

Document Level Offsets
----------------------

Setting::

    "doc_offset": True
    "doc_offset": False

Set to ``True`` to incude document-level offsets in the JSON result.

Page Text
---------

Setting::

    "text": True
    "text": False

Set to ``True`` to include page-level text in the JSON result. Page-level text will always include tables
as they appear on the page.

Dots Per Inch (DPI)
-------------------

Setting::

    "dpi": True
    "dpi": False

Set to ``True`` to include the X and Y DPI in the JSON result.

Page Size
---------

Setting::

    "size": True
    "size": False

Set to ``True`` to include the width and height of the page in pixels.

Page Number
-----------

Setting::

    "page_num": True
    "page_num": False

Set to ``True`` to include the page number with the JSON result.


Block Level Settings
====================

Block Type
----------

Setting::

    "block_type": "table"
    "block_type": "text"

Set the block type to tables or text

Block Page Number
-----------------

Setting::

    "page_num": True
    "page_num": False

Set to ``True`` to return the page number that the block occurs on

Block Level Style information
-----------------------------

Setting::

    "doc_offset": True | False
    "page_offset": True | False
    "style": True | False

Include calculated style information based on token-level values

Block Level Text
----------------

Setting::

    "text": True
    "text": False

Set to ``True`` to include block level text in the JSON result

Block Position
--------------

Setting::

    "position":
        "format": "standard" | "edges" | "corners"
        ”units”: “pixels” | “percentage”

"standard" is x, y, width, height. "edges" is top, bottom, left, right. 
"corners" is top-left, top-right, bottom-left, bottom-right. In all cases the token and character 
levels will also include “baseline”

Units "percentage" is 0 - 1 normalized values. Both sets of units use the top-left corner as (0, 0)


Token Level Settings
====================

Style
-----

Setting::

    "style": True
    "style": False

Include calculated style information for the token. Example Return:: 
    
    {"bold": true, "underlined": true, "italics": true, "font_size": 14, "background_color": "hex", "text_color": "hex"}

Token Level Confidence
----------------------

Setting::

    "confidence": True
    "confidence": False

Set to ``True`` to include token-level confidence in the JSON result. Token-level confidence is
calculated from the character-level confidence values.

Token Page Number
-----------------

Setting::

    "page_num": True
    "page_num": False


Token Level Style information
-----------------------------

Setting::

    "doc_offset": True | False
    "page_offset": True | False
    "style": True | False


Token Level Text
----------------

Setting::

    "text": True
    "text": False


Token Level Position
--------------------

Setting::

    "position":
        "format": "standard" | "edges" | "corners"
        ”units”: “pixels” | “percentage”


Character Level Settings
========================

Alternative Characters
----------------------

Setting::

    "alternatives": True
    "alternatives": False

Include alternative OCR characters along with their associated confidences. Example Return::

    [{“o”: 0.1, “0”: 0.05}]

Character Level Offsets
-----------------------

Setting::

    "doc_index": True
    "doc_index": False

Similar to "offsets" but with only one value.

Other Character Level Settings
------------------------------

Settings::

    "page_index": True | False
    "block_index": True | False
    "token_index": True | False
    "text": True | False
    "style": True | False
    "confidence": True | False
    "page_num": True | False
    "position":
        "format": "standard" | "edges" | "corners"
        ”units”: “pixels” | “percentage”

The above settings serve a similar function to their token-level counterparts.


Metadata Settings
=================

Setting::

    {“FileSize” & “Pages” & ”Encrypted” & ”PageRot” & ”Title” & ”Author” & ”Creator” & ”Producer” & ”CreationDate” & ”ModDate” & ”PDFVersion” | "all"}

Include any of a variety of document metadata fields. Input format is anything that supports the in 
operation. (e.g. set, list, dict). Optionally simply pass in “all” to get all available metadata.


Pre-set Settings Detail
=======================

These are the exact settings included in the pre-sets.

Settings included in presets::

    legacy = {
        "top_level": "document",
        "document": {"text"},
        "batch_size": 1,
    }

    simple = {
        "nest": True,
        "top_level": "document",
        "native_pdf": True,
        "multiprocessing": True,
        "document": {"text"},
        "pages": {"text", "size", "dpi", "doc_offset", "page_num", "image"},
        "blocks": {"text", "position", "doc_offset", "page_offset"},
        "batch_size": 1,
    }

    detailed = {
        "nest": True,
        "top_level": "document",
        "reblocking": {"style", "list", "inline-header"},
        "metadata": {"all"},
        "multithreading": False,
        "document": {"text"},
        "pages": {"image", "doc_offset", "text", "dpi", "size", "page_num"},
        "blocks": {"block_type", "doc_offset", "text", "style", "position"},
        "tokens": {"text", "page_num", "position", "style", "doc_offset", "confidence"},
        "chars": {"text", "position", "confidence", "doc_index", "alternate_ocr"},
        "batch_size": 1,
    }
