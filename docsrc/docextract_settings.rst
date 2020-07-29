DocumentExtraction Settings
***************************

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
and ``detailed``.

Most users will only need to use "standard" to get both document and page-level text and block positions in
a nested response format (returned object is a nested dictionary).

The "simple" configuration provides a basic and fast (3-5x faster) OCR option for native PDFs- i.e. it will
*not* work with scanned documents. Returns document, page, and block-level text and the returned object is a
nested dictionary.

The "legacy" configuration is principally intended for users who ran Indico's original pdf_extraction function to extract
text and train models. Use "legacy" if you are adding samples to models that were trained with data using
the original pdf_extraction. It returns a dictionary containing only the extracted text at the document-level.

The "detailed" configuration provides OCR metrics and details down to the character level- it's a lot of data.
In addition to document, page, and block-level text, it provides information on the text font/size,
confidence level for extracted characters, alternative characters (i.e. second most probable character), character
position information, and more. It returns a nested dictionary.

"ondocument" provides similar information to "detailed" but does not include text/metadata at the
document-level. It returns a list of dictionaries where each dictionary is page data. This preset configuration
also supports an additional "vdp" attribute, which, if set to True, performs an additional block classification
and association step. The former adds a "label_type" to every block, and the latter adds an "associations"
attribute to the result (located on the first page). The possible block classifications are the following:
- content
- table
- header
- page_header
- page_footer
- document_title

The exact settings included in "legacy", "simple", "ondocument", "standard", and "detailed"
are shown at the bottom of this page.

Result Granularity
------------------

Setting::

    "top_level": "page"
    "top_level": "document" (default)

The "document" kwarg will return a nested dictionary with text data at both the page and document level
(i.e. text data at the page-level *and* the full document text). The "page" kwarg will return
a list of dictionaries where each dictionary is page-level text data and no document-level data is included.

Nesting
-------

Setting::

    "nest": True (default)
    "nest": False

Set to ``True`` to nest the dictionary results or ``False`` to unnest them.
(i.e. nested- {“pages”: [{“blocks”:}]} *or*  unnested- {“pages”: [], “blocks”: [],})

Parse Order
-----------

Setting::

    "single_column": True (default)
    "single_column": False

Set to ``True`` to have the document parsed top to bottom as a single column of text.

Tables
----------------

Setting::

    "table_read_order": "row" (default)
    "table_read_order": "column"

You can read tables by either row or column.

By including a ``cells`` argument you can additionally receive a structured table cell output:

Setting::

    "cells": {
        "text",
        "page_num",
        "position",
        "style",
        "doc_offset",
        "page_offset",
        "block_offset",
        "row_start",
        "row_end",
        "col_start",
        "col_end"
    }

All of the above are valid options for the cell key.  This closely mimics the valid options for "blocks" but adds "row_start", "row_end", "col_start", and "col_end" as additional options.  Those fields communicate the range of spreadsheet entries that a detected cell spans. A single cell in the upper-left corner of a table would have those values set to:

    {"row_start": 0, "col_start": 0, "row_end": 0, "col_end": 0}

The end of the row and column ranges are inclusive rather than exclusive.


Force Render
------------

Setting::

    "force_render": True
    "force_render": False (default)

Force rendering of the document. Beware of increased computation cost for increased reliability of page rendering.
Only use this setting if you know you’ve got a problem that requires it.

Native PDF
----------

Setting::

    "native_pdf: True
    "native_pdf": False (default)

Set to ``True`` if you are certain that you are processing only native PDFs for a 3-5X performance increase.

Reblocking
----------

Setting::

    "reblocking": ["style", "lists"]

Whether we should use a page-level reblocking strategy that can utilize style information, or
specifically handle list-like documents well, or both.


Document Level Settings
=======================

Document Text
-------------

Setting::

    "text": True
    "text": False

Set to ``True`` to include whole document-level text in the result. Document-level text will always include tables
as they appear on the page.


Page Level Settings
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

If the "block_type" key is included, "block" objects returned in the result will contain an indicator that
records whether they were detected to be vanilla text or tabular information:

Returns::

    "block_type": "table"
    "block_type": "text"

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

    "position": True
    "position": False

Returns: top, left, bottom, right, bbTop, bbLeft, bbRight, bbBot. The values without a "bb"
prefix are "tight" bounding boxes, close to the character boundaries. The values prefixed
with "bb" are looser bounding boxes where tops and bottoms are consistent throughout a line,
and the left and right boundaries between characters won't have pixel gaps within a token.


Token Level Settings
====================

Style
-----

Setting::

    "style": True
    "style": False

Return style information for the token. Example Return::

    {"bold": true, "underlined": true, "italics": true, "font_size": 14, "background_color": <hex> color value, "text_color": <hex> color value}

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

    "position": True
    "position": False


Character Level Settings
========================

Alternative Characters
----------------------

Setting::

    "alternatives": True
    "alternatives": False

Include alternative OCR characters.

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
    "position": True | False

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
        "document": ["text"],
    }

    simple = {
        "nest": True,
        "top_level": "document",
        "native_pdf": True,
        "document": ["text"],
        "pages": ["text", "size", "dpi", "doc_offset", "page_num", "image"],
        "blocks": ["text", "position", "doc_offset", "page_offset"],
    }

    detailed = {
        "nest": True,
        "top_level": "document",
        "reblocking": ["style", "list", "inline-header"],
        "metadata": ["all"],
        "document": ["text"],
        "pages": ["image", "doc_offset", "text", "dpi", "size", "page_num"],
        "blocks": ["block_type", "doc_offset", "text", "style", "position"],
        "cells": {"text", "page_num", "position", "style", "doc_offset", "page_offset", "block_offset", "row_start", "row_end", "col_start", "col_end"},
        "tokens": ["text", "page_num", "position", "style", "doc_offset", "confidence"],
        "chars": ["text", "position", "confidence", "doc_index", "alternate_ocr"],
    }

    standard = {
        "nest": True,
        "top_level": "document",
        "native_pdf": False,
        "document": ["text"],
        "pages": ["text", "doc_offset", "page_num"],
        "blocks": ["text", "position", "doc_offset", "page_offset"],
    }

    ondocument = {
        "top_level": "page",
        "nest": False,
        "reblocking": ["style", "list", "inline-header"],
        "pages": ["text", "size", "dpi", "doc_offset", "page_num", "image", "thumbnail"],
        "blocks": ["text", "doc_offset", "page_offset", "position", "block_type", "page_num"],
        "tokens": ["text", "doc_offset", "page_offset", "block_offset", "position", "page_num", "style"],
        "chars": ["text", "doc_index", "block_index", "page_index", "page_num", "position"],
    }
