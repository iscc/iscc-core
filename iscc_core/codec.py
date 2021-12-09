# -*- coding: utf-8 -*-
"""
The `iscc_core.codec` module provides encoding, decoding and transcoding related functions.

#ISCC Component Structure:

**Header:** `<type> <subtype> <version> <length>` each coded as a variable-length 4-bit
sequence.

**Body:** `<hash-digest>` with number of bits as indicated by `<length>`
"""
import enum
import math
import mmap
from io import BufferedReader, BytesIO
from os import urandom
from random import choice
from typing import BinaryIO, List, Tuple, Union
import uvarint
from bitarray import bitarray, frozenbitarray
from bitarray._util import count_xor
from bitarray.util import ba2hex, int2ba, ba2int
from base64 import b32encode, b32decode

try:
    from pybase64 import urlsafe_b64encode, urlsafe_b64decode
except ImportError:
    from base64 import urlsafe_b64encode, urlsafe_b64decode


########################################################################################
# Type definitions                                                                     #
########################################################################################


class MT(enum.IntEnum):
    """ISCC MainTypes"""

    META = 0
    SEMANTIC = 1
    CONTENT = 2
    DATA = 3
    INSTANCE = 4
    ISCC = 5
    ID = 6


class ST(enum.IntEnum):
    """Generic SubTypes"""

    NONE = 0


class ST_CC(enum.IntEnum):
    """SubTypes for ISCC-Codes and Content-Codes"""

    TEXT = 0
    IMAGE = 1
    AUDIO = 2
    VIDEO = 3
    MIXED = 4
    NONE = 5


class ST_ID(enum.IntEnum):
    """SubTypes for ISCC-IDs"""

    PRIVATE = 0
    BITCOIN = 1
    ETHEREUM = 2


class VS(enum.IntEnum):
    """ISCC code Versions"""

    V0 = 0


class LN(enum.IntEnum):
    """ISCC length in bits"""

    L32 = 32
    L64 = 64
    L128 = 128
    L256 = 256


Data = Union[bytes, bytearray, memoryview]
Stream = Union[BinaryIO, mmap.mmap, BytesIO, BufferedReader]
IsccTuple = Tuple[
    Union[int, MT], Union[int, ST, ST_CC, ST_ID], Union[int, VS], Union[int, LN], bytes
]
AnyISCC = Union[str, IsccTuple, bytes, "Code"]


########################################################################################
# Core codec functions                                                                 #
########################################################################################


def write_header(mtype, stype, version=0, length=64):
    # type: (int, int, int, int) -> bytes
    """
    Encodes header values with nibble-sized (4-bit) variable-length encoding.
    The result is minimum 2 and maximum 8 bytes long. If the final count of nibbles
    is uneven it is padded with 4-bit `0000` at the end.

    :param int mtype: Main-type of component.
    :param int stype: Sub-type of component.
    :param int version: Version of component algorithm.
    :param int length: Length of component in number of bits (multiple of 32)
    :return: Byte encoded ISCC header.
    :rtype: bytes

    """
    if mtype == MT.ID:
        # ISCC-ID length denotes the number of bytes of the trailing counter
        assert length >= 64, "ISCC-ID minimum length 64-bits".format(length)
        length_code = (length - 64) // 8
    else:
        assert length >= 32 and not length % 32, "Length must be a multiple of 32"
        length_code = (length // 32) - 1
    header = bitarray()
    for n in (mtype, stype, version, length_code):
        header += _write_varnibble(n)
    # Append zero-padding if required (right side, least significant bits).
    header.fill()
    return header.tobytes()


def read_header(data):
    # type: (bytes) -> Tuple[int, int, int, int, bytes]
    """
    Decodes varnibble encoded header and returns it together with hash bytes.
    :param bytes data: ISCC bytes digest
    :return: (type, subtype, version, length, hash bytes)
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

    if result[0] == MT.ID:
        bit_length = 64 + (length * 8)
    else:
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


def encode_base64(data: bytes) -> str:
    """
    Standard RFC4648 base64url encoding without padding.
    """
    code = urlsafe_b64encode(data).decode("ascii")
    return code.rstrip("=")


def decode_base64(code: str) -> bytes:
    """
    Standard RFC4648 base64url decoding without padding.
    """
    padding = 4 - (len(code) % 4)
    string = code + ("=" * padding)
    return urlsafe_b64decode(string)


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


########################################################################################
# Convenience functions and classes                                                    #
########################################################################################


def encode_component(mtype, stype, version, length, digest):
    # type: (int, int, int, int, bytes) -> str
    """Encode a ISCC component inlcuding header and body with standard base32 encoding.

    !!! note
        If `digest` has more bits than specified by `length` it wil be truncated.

    :param int mtype: Main-type of component.
    :param int stype: Sub-type of component.
    :param int version: Version of component algorithm.
    :param int length: Length of component in number of bits (multiple of 32)
    :param bytes digest: The hash digest of the component.
    :return: Base32 encoded component code.
    :rtype: str
    """
    nbytes = length // 8
    header = write_header(mtype, stype, version, length)
    body = digest[:nbytes]
    component_code = encode_base32(header + body)
    return component_code


def clean(iscc):
    # type: (str) -> str
    """Cleanup ISCC String.

    Removes leading scheme and dashes.
    """
    return iscc.split(":")[-1].strip().replace("-", "")


class Code:
    """Convenience class to handle different representations of an ISCC code."""

    def __init__(self, code):
        # type: (AnyISCC) -> None
        """Initialize a Code object from any kind of representation of an ISCC.

        :param AnyISCC code: Any valid representation of an ISCC
        """
        self._head = None
        self._body = None

        if isinstance(code, Code):
            code_fields = code._head + (code.hash_bytes,)
        elif isinstance(code, str):
            code_fields = read_header(decode_base32(code))
        elif isinstance(code, tuple):
            code_fields = code
        elif isinstance(code, bytes):
            code_fields = read_header(code)
        else:
            raise ValueError(f"Code must be str, bytes, tuple or Code not {type(code)}")

        self._head = code_fields[:-1]
        body = bitarray()
        body.frombytes(code_fields[-1])
        self._body = frozenbitarray(body)

    def __str__(self):
        return self.code

    def __repr__(self):
        return f'Code("{self.code}")'

    def __bytes__(self):
        return self.bytes

    def __iter__(self):
        for f in self._head:
            yield f
        yield self.hash_bytes

    @property
    def code(self) -> str:
        """Standard base32 representation of an ISCC code."""
        return encode_base32(self.bytes)

    @property
    def bytes(self) -> bytes:
        """Raw bytes of code (including header)."""
        return self.header_bytes + self._body.tobytes()

    @property
    def hex(self) -> str:
        """Hex representation of code (including header)."""
        return self.bytes.hex()

    @property
    def uint(self) -> int:
        """Integer representation of code (including header)"""
        return int.from_bytes(self.bytes, "big", signed=False)

    @property
    def type_id(self) -> str:
        """A unique composite type-id (use as name to index codes seperately)."""
        return (
            f"{self.maintype.name}-"
            f"{self.subtype.name}-"
            f"{self.version.name}-"
            f"{self.length}"
        )

    @property
    def explain(self) -> str:
        """Human readble representation of code header."""
        if self.maintype == MT.ID:
            counter_bytes = self.hash_bytes[8:]
            if counter_bytes:
                counter = uvarint.decode(counter_bytes)
                return f"{self.type_id}-{self.hash_bytes[:8].hex()}-{counter.integer}"
        return f"{self.type_id}-{self.hash_hex}"

    @property
    def hash_bytes(self) -> bytes:
        """Byte representation of code (without header)"""
        return self._body.tobytes()

    @property
    def hash_hex(self) -> str:
        """Hex string representation of code (without header)."""
        return ba2hex(self._body)

    @property
    def hash_bits(self) -> str:
        """String of 0,1 representing the bits of the code (without header)."""
        return self._body.to01()

    @property
    def hash_ints(self) -> List[int]:
        """List of 0,1 integers representing the bits of the code (without header)."""
        return self._body.tolist(True)

    @property
    def hash_uint(self) -> int:
        """Unsinged integer representation of the code (without header)."""
        return ba2int(self._body, signed=False)

    @property
    def hash_ba(self) -> frozenbitarray:
        """Bitarray object of the code (without header)."""
        return self._body

    @property
    def header_bytes(self) -> bytes:
        """Byte representation of header prefix of the code"""
        return write_header(*self._head)

    @property
    def maintype(self) -> MT:
        """Enum maintype of code."""
        return MT(self._head[0])

    @property
    def subtype(self) -> Union[ST, ST_CC, ST_ID]:
        """Enum subtype of code."""
        if self.maintype in (MT.CONTENT, MT.ISCC):
            return ST_CC(self._head[1])
        elif self.maintype == MT.ID:
            return ST_ID(self._head[1])
        return ST(self._head[1])

    @property
    def version(self) -> VS:
        """Enum version of code."""
        return VS(self._head[2])

    @property
    def length(self) -> int:
        """Length of code hash in number of bits (without header)."""
        lengt_code = self._head[3]
        return self._head[3]

    @classmethod
    def rnd(cls, mt=None, bits=64, data=None):
        """Returns a syntactically correct random code (no MT.ID support yet)"""

        # MainType
        main_types = list(MT)
        main_types.remove(MT.ID)
        mt = choice(main_types) if mt is None else mt

        # SubType
        if mt == MT.CONTENT:
            st = choice(list(ST_CC))
        else:
            st = choice(list(ST))

        # Version
        vs = VS.V0

        # Length
        ln = bits or choice(list(LN)).value

        # Body
        data = urandom(ln // 8) if data is None else data

        return cls((mt, st, vs, ln, data))

    def __xor__(self, other) -> int:
        """Use XOR operator for hamming distance calculation."""
        return count_xor(self._body, other._body)

    def __eq__(self, other):
        # type: (Code) -> bool
        return self.code == other.code

    def __hash__(self):
        return self.uint


def decompose(iscc_code):
    # type: (str) -> List[str]
    """Decompose an ISCC into a list of singular componet codes."""

    iscc_code = clean(iscc_code)
    components = []
    raw_code = decode_base32(iscc_code)
    while raw_code:
        mt, st, vs, ln, body = read_header(raw_code)
        if mt == MT.ISCC:
            if st == ST_CC.NONE:
                # Body is Data + Instance Code
                cl = ln // 2
                data_code = encode_component(MT.DATA, ST.NONE, vs, cl, body[: cl // 8])
                instance_code = encode_component(
                    MT.INSTANCE, ST.NONE, vs, cl, body[cl // 8 :]
                )
                components.extend([data_code, instance_code])
            elif ln == 192:
                # Body is Content + Data + Instance Code
                content_code = encode_component(MT.CONTENT, st, vs, 64, body[:8])
                data_code = encode_component(MT.DATA, ST.NONE, vs, 64, body[8:16])
                instance_code = encode_component(
                    MT.INSTANCE, ST.NONE, vs, 64, body[16:24]
                )
                components.extend([content_code, data_code, instance_code])
            elif ln == 256:
                # Body is Meta + Content + Data + Instance Code
                meta_code = encode_component(MT.META, ST.NONE, vs, 64, body[:8])
                content_code = encode_component(MT.CONTENT, st, vs, 64, body[8:16])
                data_code = encode_component(MT.DATA, ST.NONE, vs, 64, body[16:24])
                instance_code = encode_component(
                    MT.INSTANCE, ST.NONE, vs, 64, body[24:32]
                )
                components.extend([meta_code, content_code, data_code, instance_code])
            else:
                raise ValueError(f"Invalid ISCC: {iscc_code}")
            raw_code = body[ln // 8 :]
        else:
            nbytes = ln // 8
            body, raw_code = body[:nbytes], body[nbytes:]
            component = encode_component(mt, st, vs, ln, body)
            components.append(component)
    return components
