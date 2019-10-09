"""
Handles deserialization / decoding of responses
"""
from collections import defaultdict
import cgi
import json
import logging
import msgpack
import traceback

from indicoio.errors import IndicoDecodingError

logger = logging.getLogger(__name__)


def deserialize(response):
    content_type, params = cgi.parse_header(response.headers.get("Content-Type"))
    charset = params.get("charset", "utf-8")
    try:
        return _SERIALIZATINON_FNS[content_type](response.content, charset)
    except Exception:
        logger.debug(traceback.format_exc())
        raise IndicoDecodingError(
            content_type, charset, response.content.decode("ascii", "ignore")
        )


def msgpack_deserialization(content, charset):
    return msgpack.unpackb(content)


def json_deserialization(content, charset="utf-8"):
    return json.loads(content.decode(charset))


def text_deserialization(content, charset="utf-8"):
    return content.decode(charset)


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
    },
)
