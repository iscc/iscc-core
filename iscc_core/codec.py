# -*- coding: utf-8 -*-
import enum
import math
import uvarint
from os import urandom
from random import choice
from typing import List, Tuple, Union
import base58
from bitarray import bitarray, frozenbitarray
from bitarray.util import ba2hex, int2ba, ba2int, count_xor
from base64 import b32encode, b32decode
from pybase64 import urlsafe_b64encode, urlsafe_b64decode


########################################################################################
# Type definitions and constants                                                       #
########################################################################################


Data = Union[bytes, bytearray, memoryview]
Stream = Union["BinaryIO", "mmap.mmap", "BytesIO", "BufferedReader"]
MainType = Union[int, "MT"]
SubType = Union[int, "ST", "ST_CC", "ST_ISCC", "ST_ID"]
Version = Union[int, "VS"]
Length = Union[int, "LN"]
Header = Tuple[MainType, SubType, Version, Length]
IsccTuple = Tuple[MainType, SubType, Version, Length, bytes]
IsccAny = Union[str, IsccTuple, bytes, "Code"]


class MT(enum.IntEnum):
    """
    ## MT - MainTypes

    | Uint | Symbol   | Bits | Purpose                                                 |
    |----- |:---------|------|---------------------------------------------------------|
    | 0    | META     | 0000 | Match on metadata similarity                            |
    | 1    | SEMANTIC | 0001 | Match on semantic content similarity                    |
    | 2    | CONTENT  | 0010 | Match on perceptual content similarity                  |
    | 3    | DATA     | 0011 | Match on data similarity                                |
    | 4    | INSTANCE | 0100 | Match on data identity                                  |
    | 5    | ISCC     | 0101 | Composite of two or more components with common header  |
    | 6    | ID       | 0110 | Short unique identifier bound to ISCC, timestamp, pubkey|
    """

    META = 0
    SEMANTIC = 1
    CONTENT = 2
    DATA = 3
    INSTANCE = 4
    ISCC = 5
    ID = 6


class ST(enum.IntEnum):
    """
    ## ST - SubTypes

    | Uint | Symbol   | Bits | Purpose                                                 |
    |----- |:---------|------|---------------------------------------------------------|
    | 0    | NONE     | 0000 | For MainTypes that do not specify SubTypes              |
    """

    NONE = 0


class ST_CC(enum.IntEnum):
    """
    ### ST_CC

    SubTypes for `MT.CONTENT`

    | Uint | Symbol   | Bits | Purpose                                                 |
    |----- |:---------|------|---------------------------------------------------------|
    | 0    | TEXT     | 0000 | Match on syntactic text similarity                      |
    | 1    | IMAGE    | 0001 | Match on perceptual image similarity                    |
    | 2    | AUDIO    | 0010 | Match on audio chroma similarity                        |
    | 3    | VIDEO    | 0011 | Match on perceptual similarity                          |
    | 4    | MIXED    | 0100 | Match on similarity of content codes                    |
    """

    TEXT = 0
    IMAGE = 1
    AUDIO = 2
    VIDEO = 3
    MIXED = 4


class ST_ISCC(enum.IntEnum):
    """
    ### ST_ISCC

    SubTypes for `MT.ISCC`

    | Uint | Symbol   | Bits | Purpose                                                 |
    |----- |:---------|------|---------------------------------------------------------|
    | 0    | TEXT     | 0000 | Composite ISCC inlcuding Text-Code                      |
    | 1    | IMAGE    | 0001 | Composite ISCC inlcuding Image-Code                     |
    | 2    | AUDIO    | 0010 | Composite ISCC inlcuding Audio-Code                     |
    | 3    | VIDEO    | 0011 | Composite ISCC inlcuding Video-Code                     |
    | 4    | MIXED    | 0100 | Composite ISCC inlcuding Mixed-Code                     |
    | 5    | SUM      | 0101 | Composite ISCC inlcuding only Data- and Instance-Code   |
    """

    TEXT = 0
    IMAGE = 1
    AUDIO = 2
    VIDEO = 3
    MIXED = 4
    SUM = 5


class ST_ID(enum.IntEnum):
    """
    ### ST_ID

    SubTypes for `MT.ID`

    | Uint | Symbol   | Bits | Purpose                                                 |
    |----- |:---------|------|---------------------------------------------------------|
    | 0    | PRIVATE  | 0000 | ISCC-ID minted via private repository (not unique)      |
    | 1    | BITCOIN  | 0001 | ISCC-ID minted via Bitcoin mainchain                    |
    | 2    | ETHEREUM | 0010 | ISCC-ID minted via Ethereum mainchain                   |
    """

    PRIVATE = 0
    BITCOIN = 1
    ETHEREUM = 2


class VS(enum.IntEnum):
    """
    ## VS - Version

    Code Version

    | Uint | Symbol   | Bits | Purpose                                                 |
    |----- |:---------|------|---------------------------------------------------------|
    | 0    | V0       | 0000 | Initial Version of Code without breaking changes        |

    """

    V0 = 0


class LN(enum.IntEnum):
    """
    ## LN - Length

    Valid lengths for hash-digests.
    """

    L32 = 32
    L64 = 64
    L72 = 72
    L80 = 80
    L96 = 96
    L128 = 128
    L160 = 160
    L192 = 192
    L224 = 224
    L256 = 256


class MULTIBASE(str, enum.Enum):
    """
    Supported Multibase encodings.
    """

    base16 = "f"
    base32 = "b"
    base58btc = "z"
    base64url = "u"


# Possible combinations of ISCC units for the first 3 components of MT.ISCC
UNITS = (
    tuple(),
    (MT.CONTENT,),
    (MT.SEMANTIC,),
    (MT.CONTENT, MT.SEMANTIC),
    (MT.META,),
    (MT.META, MT.CONTENT),
    (MT.META, MT.SEMANTIC),
    (MT.META, MT.SEMANTIC, MT.META.CONTENT),
)


########################################################################################
# Core codec functions                                                                 #
########################################################################################


def encode_component(mtype, stype, version, bit_length, digest):
    # type: (MainType, SubType, Version, Length, bytes) -> str
    """
    Encode an ISCC component inlcuding header and body with standard base32 encoding.

    !!! note
        The `length` value must be the **length in number of bits** for the component.
        If `digest` has more bits than specified by `length` it wil be truncated.


    :param MainType mtype: Maintype of component (0-6)
    :param SubType stype: SubType of component depending on MainType (0-5)
    :param Version version: Version of component algorithm (0).
    :param length bit_length: Length of component in number of bits (multiple of 32)
    :param bytes digest: The hash digest of the component.
    :return: Base32 encoded component code.
    :rtype: str
    """
    if mtype in (MT.META, MT.SEMANTIC, MT.CONTENT, MT.DATA, MT.INSTANCE, MT.ID):
        encoded_length = encode_length(mtype, bit_length)
    elif mtype == MT.ISCC:
        raise ValueError(f"{mtype} is not a unit")
    else:
        raise ValueError(f"Illegal MainType {mtype}")

    nbytes = bit_length // 8
    header = write_header(mtype, stype, version, encoded_length)
    body = digest[:nbytes]
    component_code = encode_base32(header + body)
    return component_code


def write_header(mtype, stype, version=0, length=1):
    # type: (MainType, SubType, Version, Length) -> bytes
    """
    Encodes header values with nibble-sized (4-bit) variable-length encoding.
    The result is minimum 2 and maximum 8 bytes long. If the final count of nibbles
    is uneven it is padded with 4-bit `0000` at the end.

    !!! warning
        The length value must be encoded beforhand because its semantics depend on
        the MainType (see `encode_length` function).

    :param MainType mtype: MainType of component.
    :param SubType stype: SubType of component.
    :param Version version: Version of component algorithm.
    :param Length length: length value of component (1 means 64-bits for standard units)
    :return: Varnibble stream encoded ISCC header as bytes.
    :rtype: bytes

    """
    # TODO verify that all header params and there combination is valid
    header = bitarray()
    for n in (mtype, stype, version, length):
        header += write_varnibble(n)
    # Append zero-padding if required (right side, least significant bits).
    header.fill()
    return header.tobytes()


def write_varnibble(n):
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

    :param int n: Positive integer to be encoded as varnibble (0-4679)
    :return: Varnibble encoded integera
    :rtype: bitarray
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


def read_header(data):
    # type: (bytes) -> IsccTuple
    """
    Decodes varnibble encoded header and returns it together with `tail data`.

    Tail data is included to enable decoding of sequential ISCCs. The returned tail
    data must be truncated to decode_length(r[0], r[3]) bits to recover the actual
    hash-bytes.

    :param bytes data: ISCC bytes
    :return: (MainType, SubType, Version, length, TailData)
    :rtype: IsccTuple
    """
    result = []
    ba = bitarray()
    ba.frombytes(data)
    data = ba
    for _ in range(4):
        value, data = read_varnibble(data)
        result.append(value)

    # TODO: validate correctness of decoded data.

    # Strip 4-bit padding if required
    if len(data) % 8 and data[:4] == bitarray("0000"):
        data = data[4:]

    result.append(data.tobytes())

    return tuple(result)


def read_varnibble(b):
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


def encode_units(units):
    # type: (Tuple) -> int
    """
    Encodes a combination of ISCC units to an integer between 0-7 to be used as length
    value for the final encoding of MT.ISCC
    """
    return UNITS.index(units)


def decode_units(unit_id):
    # type: (int) -> Tuple[MT, ...]
    """
    Decodes an ISCC header length value that has been encoded with a unit_id to an
    ordered tuple of MainTypes.
    """
    units = sorted(UNITS[unit_id])
    return tuple(MT(u) for u in units)


def encode_length(mtype, length):
    # type: (MainType, Length) -> int
    """
    Encode length to integer value for header encoding.

    The `length` value has MainType-specific semantics:

    MainTypes `META`, `SEMANTIC`, `CONTENT`, `DATA`, `INSTANCE`:
        Length means number of bits for the body.
        Length is encoded as number of 32-bit chunks (0 being 32bits)
        Examples: 32 -> 0, 64 -> 1, 96 -> 2 ...

    MainType `ID`:
        Lengths means number the number of bits for the body including the counter
        Length is encoded as number of bytes of the counter (64-bit body is implicit)
        Examples:
            64 -> 0 (No counter)
            72 -> 1 (One byte counter)
            80 -> 2 (Two byte counter)
            ...

    MainType `ISCC`:
        Length means the composition of optional 64-bit components included in the ISCC
        Examples:
            No optional components -> 0000 -> 0
            CONTENT                -> 0001 -> 1
            SEMANTIC               -> 0010 -> 2
            SEMANTIC, CONTENT      -> 0011 -> 3
            META                   -> 0100 -> 4
            META, CONTENT          -> 0101 -> 5
            ...

    :param MainType mtype: The MainType for which to encode the length value.
    :param Length length: The length expressed according to the semantics of the type
    :return: The length value encoded as integer for use with write_header.
    """

    error = f"Invalid length {length} for MainType {mtype}"
    # standard case (length field denotes number of 32-bit chunks, 0 being 32-bits)
    if mtype in (MT.META, MT.SEMANTIC, MT.CONTENT, MT.DATA, MT.INSTANCE):
        if length >= 32 and not length % 32:
            return (length // 32) - 1
        raise ValueError(error)
    # flag type encoding of included components (pass through as encoded out-of-band)
    elif mtype == MT.ISCC:
        if 0 <= length <= 7:
            return length
        raise ValueError(error)
    # counter byte lenght encoding
    elif mtype == MT.ID:
        if 64 <= length <= 96:
            return (length - 64) // 8
        raise ValueError(error)
    else:
        raise ValueError(error)


def decode_length(mtype, length):
    # type: (MainType, Length) -> LN
    """
    Dedoce raw length value from ISCC header to length of digest in number of bits.

    Decodes a raw header integer value in to its semantically meaningfull value (eg.
    number of bits)
    """
    if mtype in (MT.META, MT.SEMANTIC, MT.CONTENT, MT.DATA, MT.INSTANCE):
        return LN((length + 1) * 32)
    elif mtype == MT.ISCC:
        return LN(len(decode_units(length)) * 64 + 128)
    elif mtype == MT.ID:
        return LN(length * 8 + 64)
    else:
        raise ValueError(f"Invalid length {length} for MainType {mtype}")


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


def decompose(iscc_code):
    # type: (str) -> List[str]
    """
    Decompose an ISCC-CODE or any valid ISCC sequence into a list of ISCC-UNITS.

    A valid ISCC sequence is a string concatenation of ISCC-UNITS optionally seperated
    by a hyphen.
    """

    iscc_code = clean(iscc_code)
    components = []

    raw_code = decode_base32(iscc_code)
    while raw_code:
        mt, st, vs, ln, body = read_header(raw_code)
        # standard ISCC-UNIT with tail continuation
        if mt != MT.ISCC:
            ln_bits = decode_length(mt, ln)
            code = encode_component(mt, st, vs, ln_bits, body[: ln_bits // 8])
            components.append(code)
            raw_code = body[ln_bits // 8 :]
            continue

        # ISCC-CODE
        main_types = decode_units(ln)

        # rebuild dynamic units (META, SEMANTIC, CONTENT)
        for idx, mtype in enumerate(main_types):
            stype = ST.NONE if mtype == MT.META else st
            code = encode_component(mtype, stype, vs, 64, body[idx * 8 :])
            components.append(code)

        # rebuild static units (DATA, INSTANCE)
        data_code = encode_component(MT.DATA, ST.NONE, vs, 64, body[-16:-8])
        instance_code = encode_component(MT.INSTANCE, ST.NONE, vs, 64, body[-8:])
        components.extend([data_code, instance_code])
        break

    return components


def normalize(iscc_code):
    # type: (str) -> str
    """
    Normalize an ISCC to its canonical URI form.

    The canonical form of an ISCC is its shortest base32 encoded representation
    prefixed with the string `ISCC:`.

    Possible valid inputs:
        MEACB7X7777574L6
        ISCC:MEACB7X7777574L6
        fcc010001657fe7cafe9791bb
        iscc:maagztfqttvizpjr
        Iscc:Maagztfqttvizpjr


    !!! info
        A concatenated sequence of codes will be composed into a single ISCC of MainType
        `MT.ISCC` if possible.

    !!! example
        ``` py
        >>> import iscc_core
        >>> iscc_core.normalize("GAAW2PRCRS5LNVZV-IAAUVACQKXE3V44W")
        ISCC:KUBW2PRCRS5LNVZVJKAFAVOJXLZZM
        ```

    :param str iscc_code: Any valid ISCC string
    :return: Normalized ISCC
    :rtype: str
    """
    from iscc_core.iscc_code import gen_iscc_code_v0

    decoders = {
        MULTIBASE.base16: bytes.fromhex,  # f
        MULTIBASE.base32: decode_base32,  # b
        MULTIBASE.base58btc: base58.b58decode,  # z
        MULTIBASE.base64url: decode_base64,  # u
    }

    # Transcode to base32 if <multibase><multicodec> encoded
    multibase_prefix = iscc_code[0]
    if multibase_prefix in decoders.keys():
        decoder = decoders[multibase_prefix]
        decoded = decoder(iscc_code[1:])
        if not decoded.startswith(Code.mc_prefix):
            raise ValueError(f"Malformed multiformat codec: {decoded[:2]}")
        iscc_code = encode_base32(decoded[2:])

    decomposed = decompose(iscc_code)
    recomposed = (
        gen_iscc_code_v0(decomposed).iscc if len(decomposed) >= 2 else decomposed[0]
    )
    return f"ISCC:{recomposed}"


########################################################################################
# Convenience functions and classes                                                    #
########################################################################################


def clean(iscc):
    # type: (str) -> str
    """
    Cleanup ISCC string.

    Removes leading scheme, dashes, leading/trailing whitespace.

    :param str iscc: Any valid ISCC string
    :return: Cleaned ISCC string.
    :rtype: str
    """
    split = [part.strip() for part in iscc.strip().split(":")]
    if len(split) == 1:
        code = split[0]
        # remove dashes if not multiformat
        if code[0] not in list(MULTIBASE):
            code = code.replace("-", "")
        return code
    elif len(split) == 2:
        scheme, code = split
        if scheme.lower() != "iscc":
            raise ValueError(f"Invalid scheme: {scheme}")
        return code.replace("-", "")
    else:
        raise ValueError(f"Malformed ISCC string: {iscc}")


class Code:
    """
    Convenience class to handle different representations of an ISCC.
    """

    #: Multicodec prefix code
    mc_prefix: bytes = b"\xcc\x01"

    def __init__(self, code):
        # type: (IsccAny) -> None
        """
        Initialize a Code object from any kind of representation of an ISCC.

        :param AnyISCC code: Any valid representation of an ISCC
        """
        self._head = None
        self._body = None

        if isinstance(code, Code):
            code_fields = code._head + (code.hash_bytes,)
        elif isinstance(code, str):
            # code = clean(code)
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
    def uri(self) -> str:
        """Standard uri representation of an ISCC code."""
        return f"iscc:{self.code.lower()}"

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
        if self.maintype == MT.ISCC:
            mtypes = decode_units(self._head[3])
            length = "".join([t.name[0] for t in mtypes]) + "DI"
        else:
            length = self.length
        return (
            f"{self.maintype.name}-"
            f"{self.subtype.name}-"
            f"{self.version.name}-"
            f"{length}"
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
    def subtype(self) -> Union[ST, ST_CC, ST_ISCC, ST_ID]:
        """Enum subtype of code."""
        if self.maintype == MT.CONTENT:
            return ST_CC(self._head[1])
        elif self.maintype == MT.ISCC:
            return ST_ISCC(self._head[1])
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
        return decode_length(self._head[0], self._head[3])

    @classmethod
    def rnd(cls, mt=None, st=None, bits=64, data=None):
        """Returns a syntactically correct random code."""

        # MainType
        mt = choice(list(MT)) if mt is None else mt

        # SubType
        if st is None:
            if mt == MT.CONTENT:
                st = choice(list(ST_CC))
            elif mt == MT.ISCC:
                units = choice(UNITS)
                st = choice(list(ST_ISCC))
                st = (
                    st if (MT.SEMANTIC in units or MT.CONTENT in units) else ST_ISCC.SUM
                )
                bits = len(units) * 64 + 128
            elif mt == MT.ID:
                st = choice(list(ST_ID))
            else:
                st = choice(list(ST))

        # Version
        vs = VS.V0

        # Length
        ln_bits = bits or choice(list(LN)).value
        if mt == MT.ISCC:
            ln_code = encode_units(units)
        else:
            ln_code = encode_length(mt, bits)

        # Body
        data = urandom(ln_bits // 8) if data is None else data

        return cls((mt, st, vs, ln_code, data))

    @property
    def mc_bytes(self):
        """ISCC header + body with multicodec prefix."""
        return self.mc_prefix + self.bytes

    @property
    def mf_base16(self) -> str:
        """Multiformats base16 encoded."""
        return "f" + self.mc_bytes.hex()

    @property
    def mf_base32(self) -> str:
        """Multiformats base32 encoded."""
        return "b" + encode_base32(self.mc_bytes).lower()

    @property
    def mf_base58btc(self) -> str:
        """Multiformats base58btc encoded."""
        return "z" + base58.b58encode(self.mc_bytes).decode("ascii")

    @property
    def mf_base64url(self) -> str:
        """Multiformats base64url encoded."""
        return "u" + encode_base64(self.mc_bytes)

    # TODO: bech32m support
    # @property
    # def bech32m(self):
    #     """Encode as bech32m with hrp `iscc`"""
    #     data = [bech32.CHARSET.find(c) for c in self.code.lower()]
    #     return bech32.bech32_encode(
    #         "iscc", data, bech32.Encoding.BECH32M
    #     )

    def __xor__(self, other) -> int:
        """Use XOR operator for hamming distance calculation."""
        return count_xor(self._body, other._body)

    def __eq__(self, other):
        # type: (Code) -> bool
        return self.code == other.code

    def __hash__(self):
        return self.uint
