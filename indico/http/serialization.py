"""
Handles deserialization / decoding of responses
"""

import gzip
import json
import logging
import traceback
from collections import defaultdict
from email.message import EmailMessage
from typing import TYPE_CHECKING

from indico.errors import IndicoDecodingError

if TYPE_CHECKING:  # pragma: no cover
    from typing import Any, Callable, Dict, Mapping, Optional, Tuple

    import httpx

logger = logging.getLogger(__name__)

GZIP_CONTENT_TYPES = ("application/x-gzip", "application/gzip")


def deserialize(
    response: "httpx.Response", force_json: bool = False, force_decompress: bool = False
) -> "Any":
    content_type, params = parse_header(response.headers.get("content-type", ""))
    content: bytes = response.content

    if force_decompress or content_type in GZIP_CONTENT_TYPES:
        content = gzip.decompress(content)

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


async def aio_deserialize(
    response: "httpx.Response", force_json: bool = False, force_decompress: bool = False
) -> "Any":
    content_type, params = parse_header(response.headers.get("content-type", ""))
    content: bytes = response.content

    if force_decompress or content_type in GZIP_CONTENT_TYPES:
        content = gzip.decompress(content)

    charset: str = params.get("charset", "utf-8")

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


def parse_header(header: str) -> "Tuple[str, Dict[str, str]]":
    email = EmailMessage()
    email["Content-Type"] = header
    return email.get_content_type(), email["Content-Type"].params


def raw_bytes(
    content: bytes, charset: "Optional[str]", *args: "Any", **kwargs: "Any"
) -> bytes:
    return content


def msgpack_deserialization(content: bytes, charset: "Optional[str]" = None) -> "Any":
    try:
        import msgpack
    except ImportError as error:
        raise RuntimeError(
            "msgpack deserialization requires additional dependencies: "
            "`pip install indico-client[deserialization]`"
        ) from error

    return msgpack.unpackb(content)


def json_deserialization(content: bytes, charset: str = "utf-8") -> "Any":
    return json.loads(content.decode(charset))


def text_deserialization(content: bytes, charset: str = "utf-8") -> str:
    return content.decode(charset)


def image_serialization(content: bytes, charset: "Optional[str]" = None) -> bytes:
    return content


def zip_serialization(content: bytes, charset: "Optional[str]" = None) -> bytes:
    return content


_SERIALIZATION_FNS: "Mapping[str, Callable[[bytes, str], Any]]" = defaultdict(
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
