# -*- coding: utf-8 -*-
"""
The `iscc.codec` module provides encoding, decoding and transcoding related functions.

#ISCC Component Structure:

**Header:** `<type> <subtype> <version> <length>` each coded as a variable-length 4-bit
sequence.

**Body:** `<hash-digest>` with number of bits as indicated by `<length>`
"""
import enum
import math
from typing import Tuple
from bitarray import bitarray
from bitarray.util import int2ba, ba2int
from base64 import b32encode, b32decode

try:
    from pybase64 import urlsafe_b64encode, urlsafe_b64decode
except ImportError:
    from base64 import urlsafe_b64encode, urlsafe_b64decode


class MT(enum.IntEnum):
    """ISCC Main Types"""

    META = 0
    SEMANTIC = 1
    CONTENT = 2
    DATA = 3
    INSTANCE = 4
    ISCC = 5


class ST(enum.IntEnum):
    """Generic SubTypes"""

    NONE = 0


class ST_CC(enum.IntEnum):
    """SubTypes for Content Codes"""

    TEXT = 0
    IMAGE = 1
    AUDIO = 2
    VIDEO = 3
    GENERIC = 4


class VS(enum.IntEnum):
    """ISCC code Versions"""

    V0 = 0


class LN(enum.IntEnum):
    """ISCC lenth in bits"""

    L32 = 32
    L64 = 64
    L128 = 128
    L256 = 256


def encode_component(mtype, stype, version, length, digest):
    # type: (int, int, int, int, bytes) -> str
    """Encode an ISCC standard component.

    !!! note
        Oversized digests will be truncated to specified length.
    """
    nbytes = length // 8
    header = write_header(mtype, stype, version, length)
    body = digest[:nbytes]
    component_code = encode_base32(header + body)
    return component_code


def write_header(mtype, stype, version=0, length=64):
    # type: (int, int, int, int) -> bytes
    """
    Encodes header values with nibble-sized variable-length encoding.
    The result is minimum 2 and maximum 8 bytes long. If the final count of nibbles
    is uneven it is padded with 4-bit `0000` at the end.
    """
    assert length >= 32 and not length % 32, "Length must be a multiple of 32"
    length = (length // 32) - 1
    header = bitarray()
    for n in (mtype, stype, version, length):
        header += _write_varnibble(n)
    # Append zero-padding if required (right side, least significant bits).
    header.fill()
    return header.tobytes()


def read_header(data):
    # type: (bytes) -> Tuple[int, int, int, int, bytes]
    """
    Decodes varnibble encoded header and returns it together with remaining bytes.
    :returns: (type, subtype, version, length, remaining bytes)
    """
    result = []
    ba = bitarray()
    ba.frombytes(data)
    data = ba
    for x in range(3):
        value, data = _read_varnibble(data)
        result.append(value)

    # interpret length value
    length, data = _read_varnibble(data)

    bit_length = (length + 1) * 32
    result.append(bit_length)

    # Strip 4-bit padding if required
    if len(data) % 8 and data[:4] == bitarray("0000"):
        data = data[4:]

    result.append(data.tobytes())

    return tuple(result)


def encode_base32(data):
    # type: (bytes) -> str
    """
    Standard RFC4648 base32 encoding without padding.
    """
    return b32encode(data).decode("ascii").rstrip("=")


def decode_base32(code):
    # type: (str) -> bytes
    """
    Standard RFC4648 base32 decoding without padding and with casefolding.
    """
    # python stdlib does not support base32 without padding, so we have to re-pad.
    cl = len(code)
    pad_length = math.ceil(cl / 8) * 8 - cl

    return bytes(b32decode(code + "=" * pad_length, casefold=True))


def _write_varnibble(n):
    # type: (int) -> bitarray
    """
    Writes integer to variable length sequence of 4-bit chunks.
    Variable-length encoding scheme:
    ------------------------------------------------------
    | prefix bits | nibbles | data bits | unsigned range |
    | ----------- | ------- | --------- | -------------- |
    | 0           | 1       | 3         | 0 - 7          |
    | 10          | 2       | 6         | 8 - 71         |
    | 110         | 3       | 9         | 72 - 583       |
    | 1110        | 4       | 12        | 584 - 4679     |
    """
    if 0 <= n < 8:
        return int2ba(n, length=4)
    elif 8 <= n < 72:
        return bitarray("10") + int2ba(n - 8, length=6)
    elif 72 <= n < 584:
        return bitarray("110") + int2ba(n - 72, length=9)
    elif 584 <= n < 4680:
        return bitarray("1110") + int2ba(n - 584, length=12)
    else:
        raise ValueError("Value must be between 0 and 4679")


def _read_varnibble(b):
    # type: (bitarray) -> Tuple[int, bitarray]
    """Reads first varnibble, returns its integer value and remaining bits."""

    bits = len(b)

    if bits >= 4 and b[0] == 0:
        return ba2int(b[:4]), b[4:]
    if bits >= 8 and b[1] == 0:
        return ba2int(b[2:8]) + 8, b[8:]
    if bits >= 12 and b[2] == 0:
        return ba2int(b[3:12]) + 72, b[12:]
    if bits >= 16 and b[3] == 0:
        return ba2int(b[4:16]) + 584, b[16:]

    raise ValueError("Invalid bitarray")


def clean(iscc):
    # type: (str) -> str
    """Cleanup ISCC String.

    Removes leading scheme and dashes.
    """
    return iscc.split(":")[-1].strip().replace("-", "")
