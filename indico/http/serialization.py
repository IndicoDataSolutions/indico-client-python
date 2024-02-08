"""
Handles deserialization / decoding of responses
"""
import cgi
import gzip
import io
import json
import logging
import traceback
from collections import defaultdict

import msgpack

from indico.errors import IndicoDecodingError

logger = logging.getLogger(__name__)


def decompress(response):
    response.raw.decode_content = True
    value = io.BytesIO(response.raw.data).getvalue()
    return gzip.decompress(value)


def deserialize(response, force_json=False, force_decompress=False):
    content_type, params = cgi.parse_header(response.headers.get("Content-Type"))

    if force_decompress or content_type in ["application/x-gzip", "application/gzip"]:
        content = decompress(response)
    else:
        content = response.content

    charset = params.get("charset", "utf-8")

    # For storage object for example where the content is json based on url ending
    if force_json:
        content_type = "application/json"

    try:
        return _SERIALIZATION_FNS[content_type](content, charset)
    except Exception:
        logger.debug(traceback.format_exc())
        raise IndicoDecodingError(
            content_type, charset, content.decode("ascii", "ignore")
        )

async def aio_deserialize(response, force_json=False, force_decompress=False):
    content_type, params = cgi.parse_header(response.headers.get("Content-Type"))
    content = await response.read()

    if force_decompress or content_type in ["application/x-gzip", "application/gzip"]:
        content = gzip.decompress(io.BytesIO(content).get_value())

    charset = params.get("charset", "utf-8")

    # For storage object for example where the content is json based on url ending
    if force_json:
        content_type = "application/json"

    try:
        return _SERIALIZATION_FNS[content_type](content, charset)
    except Exception:
        logger.debug(traceback.format_exc())
        raise IndicoDecodingError(
            content_type, charset, content.decode("ascii", "ignore")
        )

def raw_bytes(content, *args, **kwargs):
    return content


def msgpack_deserialization(content, charset):
    return msgpack.unpackb(content)


def json_deserialization(content, charset="utf-8"):
    return json.loads(content.decode(charset))


def text_deserialization(content, charset="utf-8"):
    return content.decode(charset)


def image_serialization(content, charset=None):
    return content


def zip_serialization(content, charset=None):
    return content


_SERIALIZATION_FNS = defaultdict(
    lambda: text_deserialization,
    {
        "application/pdf": raw_bytes,
        "application/octet-stream": raw_bytes,
        "application/doc": raw_bytes,
        "application/ms-doc": raw_bytes,
        "application/msword": raw_bytes,
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document": raw_bytes,
        "application/vnd.oasis.opendocument.text": raw_bytes,
        "application/zip": zip_serialization,
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": raw_bytes,
        "application/vnd.ms-excel": raw_bytes,
        "application/msexcel": raw_bytes,
        "application/excel": raw_bytes,
        "application/msexcel": raw_bytes,
        "application/x-dos_ms_excel": raw_bytes,
        "application/x-excel": raw_bytes,
        "application/x-ms-excel": raw_bytes,
        "application/x-xls": raw_bytes,
        "application/xlc": raw_bytes,
        "application/xls": raw_bytes,
        "application/xlt": raw_bytes,
        "application/vnd.ms-powerpoint": raw_bytes,
        "application/vnd.openxmlformats-officedocument.presentationml.presentation": raw_bytes,
        "application/mspowerpoint": raw_bytes,
        "application/powerpoint": raw_bytes,
        "application/vnd.ms-powerpoint": raw_bytes,
        "application/x-mspowerpoint": raw_bytes,
        "image/png": image_serialization,
        "image/jpeg": image_serialization,
        "image/jpg": image_serialization,
        "image/tiff": image_serialization,
        "text/html": text_deserialization,
        "text/plain": text_deserialization,
        "text/rtf": text_deserialization,
        "message/rfc822": raw_bytes,
        "application/vnd.ms-outlook": raw_bytes,
        "application/vnd.ms-office": raw_bytes,
        "binary/octet-stream": raw_bytes,
        "application/rtf": text_deserialization,
        "text/csv": text_deserialization,
        "application/x-msgpack": msgpack_deserialization,
        "application/msgpack": msgpack_deserialization,
        "x-msgpack": msgpack_deserialization,
        "msgpack": msgpack_deserialization,
        "application/json": json_deserialization,
        "json": json_deserialization,
        "application/javascript": json_deserialization,
        "application/x-gzip": raw_bytes,
        "application/gzip": raw_bytes,
    },
)
