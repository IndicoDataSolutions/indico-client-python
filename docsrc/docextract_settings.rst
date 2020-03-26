OCR With DocumentExtraction
***************************

Introduction
============

The Indico Platform includes a sophisticated OCR engine that's capable of extracting raw
text from a variety of document formats including PDF and TIF. OCR functionality is provided
by the ``DocumentExtraction`` class. Here's how to OCR one document with DocumentExtraction::

    from indico import IndicoClient
    from indico.queries.documents import DocumentExtraction
    from indico.queries import JobStatus, RetrieveStorageObject

    # assumes you have your api token in your working or home directory
    client = IndicoClient()
    files_to_extract = client.call(DocumentExtraction(files=['./path_to_document.pdf']))
    extracted_file = client.call(JobStatus(id=files_to_extract[0].id, wait=True))
    json_result = client.call(RetrieveStorageObject(extracted_file.result))

In this example, given the path to a document, we called DocumentExtraction with a single file and waited for the result.
With most use cases, this is all you will need to do.

``DocumentExtraction`` is highly configurable. You can customize settings at the document, page, block, token or
character level. You can also choose from a selection of preset configurations. You configure DocumentExtraction
by passing in a Python dictionary or JSON string.

Here's an Example::

    my_ocr_config = {
        "preset_config": "standard"
    }

    job = client.call(DocumentExtraction(files=['./path_to_doc.pdf'], json_config=my_ocr_config))


Global Settings
===============

Preset Configurations
----------------------

Setting::

    "preset_config": "simple"
    "preset_config": "legacy"
    "preset_config": "detailed"
    "preset_config": "ondocument"
    "preset_config": "standard"

Five preset ocr configurations are provided: ``legacy``, ``simple``, ``ondocument``, ``standard``, 
and ``detailed``. Most users will only need to use "standard" to get text and block positions in 
a nested response format. "simple" provides a basic and fast (3-5x faster) OCR option for native PDFs 
(it will not work with scanned documents). "legacy" is intended for users who ran Indico's 
original pdf_extraction function to extract text and train models. Use "legacy" if you are 
adding samples to models that were trained with the original pdf_extraction. "detailed" provides 
OCR metrics and details down to the character level- it's a lot of data. "ondocument" provides 
similar information to "detailed" but at the page rather than document-level, in an unnested format, 
and without document metadata. 

The exact settings included in "legacy", "simple", "ondocument", "standard", and "detailed" 
are shown at the bottom of this page.

Result Granularity
------------------

Setting::

    "top_level": "page" (default)
    "top_level": "document"

The JSON result can be a single result for the entire document ("document") or
broken into a list with one item for each page ("page").

Parse Order
-----------

Setting::

    "single_column": True (default)
    "single_column": False

Set to ``True`` to have the document parsed top to bottom as a single column of text.

Table Read Order
----------------

Setting::

    "table_read_order": "row" (default)
    "table_read_order": "column"

You can read tables by either row or column.

Force Render
------------

Setting::

    "force_render": True
    "force_render": False (default)

Force rendering of the document. Beware of increased computation cost for increased reliability of page rendering.
Only use this setting if you know you’ve got a problem that requires it.

Reblocking
----------

Setting::

    "reblocking": ["style", "lists"]

Whether we should use a page-level reblocking strategy that can utilize style information, or
specifically handle list-like documents well, or both.


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
        "resolution": "128x165" (default)   # i.e. - <x-dimension>x<y-dimension>

Provide this setting to return page thumbnails of the specified resolution. Separate from full
sized images.

Document Level Offsets
----------------------

Setting::

    "doc_offset": True
    "doc_offset": False

Set to ``True`` to include document-level offsets in the JSON result.

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

"standard" returns position as x, y, width, height. "edges" returns top, bottom, left, right.
"corners" returns top-left, top-right, bottom-left, bottom-right. In all cases the token and character
levels will also include “baseline”

Units "percentage" is 0 - 1 normalized values. Both sets of units use the top-left corner as (0, 0)


Token Level Settings
====================

Style
-----

Setting::

    "style": True
    "style": False

Return style information for the token. Example Return::

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
        "units": "pixels" | "percentage"


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

The settings above serve a similar function to their token-level counterparts.


Metadata Settings
=================

Setting::

    {“FileSize” & “Pages” & ”Encrypted” & ”PageRot” & ”Title” & ”Author” & ”Creator” & ”Producer” & ”CreationDate” & ”ModDate” & ”PDFVersion” | "all"}

Include any of a variety of document metadata fields. Input format is anything that supports the python "in"
operation. (e.g. set, list, dict). Optionally, simply pass in “all” to get all available metadata.


Preset Configuration Details
============================

These are the exact settings included in the presets.

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
        "document": {"text"},
        "pages": {"image", "doc_offset", "text", "dpi", "size", "page_num"},
        "blocks": {"block_type", "doc_offset", "text", "style", "position"},
        "tokens": {"text", "page_num", "position", "style", "doc_offset", "confidence"},
        "chars": {"text", "position", "confidence", "doc_index", "alternate_ocr"},
        "batch_size": 1,
    }

    standard = {
        "nest": True,
        "top_level": "document",
        "native_pdf": False,
        "document": {"text"},
        "pages": {"text", "doc_offset", "page_num"},
        "blocks": {"text", "position", "doc_offset", "page_offset"},
        "batch_size": 1,
    }

    ondocument = {
        "top_level": "page",
        "nest": False,
        "reblocking": {"style", "lists", "inline-header"},
        "pages": {"text", "size", "dpi", "doc_offset", "page_num", "image", "thumbnail"},
        "blocks": {"text", "doc_offset", "page_offset", "position", "block_type", "page_num"},
        "tokens": {"text", "doc_offset", "page_offset", "block_offset", "position", "page_num", "style"},
        "chars": {"text", "doc_index", "block_index", "page_index", "page_num", "position"},
        "batch_size": 1
    }
