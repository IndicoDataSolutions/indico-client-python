"""
Handles deserialization / decoding of responses
"""
from collections import defaultdict
import cgi
import json
import io
import gzip
import logging
import msgpack
import traceback

from indico.errors import IndicoDecodingError

logger = logging.getLogger(__name__)


def decompress(response):
    response.raw.decode_content = True
    value = io.BytesIO(response.raw.data).getvalue()
    return gzip.decompress(value)


def deserialize(response, gzip=False, force_json=False):
    content_type, params = cgi.parse_header(response.headers.get("Content-Type"))

    content = None
    if gzip:
        content = decompress(response)
    else:
        content = response.content

    charset = params.get("charset", "utf-8")

    # For storage object for example where the content is json based on url ending
    if force_json:
        content_type = "application/json"

    try:
        return _SERIALIZATINON_FNS[content_type](content, charset)
    except Exception:
        logger.debug(traceback.format_exc())
        raise IndicoDecodingError(
            content_type, charset, content.decode("ascii", "ignore")
        )


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


_SERIALIZATINON_FNS = defaultdict(
    lambda: text_deserialization,
    {
        "text/html": text_deserialization,
        "application/x-msgpack": msgpack_deserialization,
        "application/msgpack": msgpack_deserialization,
        "x-msgpack": msgpack_deserialization,
        "msgpack": msgpack_deserialization,
        "application/json": json_deserialization,
        "json": json_deserialization,
        "application/javascript": json_deserialization,
        "image/png": image_serialization,
        "image/jpg": image_serialization,
        "application/zip": zip_serialization,
    },
)
