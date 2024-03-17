# -*- coding: utf-8 -*-
import math
import uvarint
from typing import List, Tuple
import base58
from bitarray import bitarray
from bitarray.util import int2ba, ba2int
from base64 import b32encode, b32decode
from pybase64 import urlsafe_b64encode, urlsafe_b64decode
from iscc_core.constants import *


########################################################################################
# Core codec functions                                                                 #
########################################################################################


def encode_component(mtype, stype, version, bit_length, digest):
    # type: (MainType, SubType, Version, Length, bytes) -> str
    """
    Encode an ISCC-UNIT inlcuding header and body with standard base32 encoding.

    !!! note
        The `length` value must be the **length in number of bits** for the component.
        If `digest` has more bits than specified by `length` it wil be truncated.


    :param MainType mtype: Maintype of unit (0-6)
    :param SubType stype: SubType of unit depending on MainType (0-5)
    :param Version version: Version of unit algorithm (0).
    :param length bit_length: Length of unit, in number of bits (multiple of 32)
    :param bytes digest: The hash digest of the unit.
    :return: Base32 encoded ISCC-UNIT.
    :rtype: str
    """
    if mtype in (MT.META, MT.SEMANTIC, MT.CONTENT, MT.DATA, MT.INSTANCE, MT.ID, MT.FLAKE):
        encoded_length = encode_length(mtype, bit_length)
    elif mtype == MT.ISCC:
        raise ValueError(f"{mtype} is not a unit")
    else:
        raise ValueError(f"Illegal MainType {mtype}")

    nbytes = bit_length // 8
    header = encode_header(mtype, stype, version, encoded_length)
    body = digest[:nbytes]
    component_code = encode_base32(header + body)
    return component_code


def encode_header(mtype, stype, version=0, length=1):
    # type: (MainType, SubType, Version, Length) -> bytes
    """
    Encodes header values with nibble-sized (4-bit) variable-length encoding.
    The result is minimum 2 and maximum 8 bytes long. If the final count of nibbles
    is uneven it is padded with 4-bit `0000` at the end.

    !!! warning
        The length value must be encoded beforhand because its semantics depend on
        the MainType (see `encode_length` function).

    :param MainType mtype: MainType of unit.
    :param SubType stype: SubType of unit.
    :param Version version: Version of component algorithm.
    :param Length length: length value of unit (1 means 64-bits for standard units)
    :return: Varnibble stream encoded ISCC header as bytes.
    :rtype: bytes

    """
    header = bitarray()
    for n in (mtype, stype, version, length):
        header += encode_varnibble(n)
    # Append zero-padding if required (right side, least-significant bits).
    header.fill()
    return header.tobytes()


def encode_varnibble(n):
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


def decode_header(data):
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
        value, data = decode_varnibble(data)
        result.append(value)

    # Strip 4-bit padding if required
    if len(data) % 8 and data[:4] == bitarray("0000"):
        data = data[4:]

    result.append(data.tobytes())

    return tuple(result)


def decode_varnibble(b):
    # type: (bitarray) -> Tuple[int, bitarray]
    """Reads first varnibble, returns its integer value and remaining bits.

    :param bitarray b: Array of header bits
    :return: A tuple of the integer value of first varnible and the remaining bits.
    :rtype: Tuple[int, bitarray]
    """

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
    # type: (Tuple[MT, ...]) -> int
    """
    Encodes a combination of ISCC units to an integer between 0-7 to be used as length
    value for the final encoding of MT.ISCC

    :param Tuple units: A tuple of a MainType combination (can be empty)
    :return: Integer value to be used as length-value for header encoding
    :rtype: int
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

    For MainTypes `META`, `SEMANTIC`, `CONTENT`, `DATA`, `INSTANCE`:

        Length means number of bits for the body.
        Length is encoded as the multiple of 32-bit chunks (0 being 32bits)
        Examples: 32 -> 0, 64 -> 1, 96 -> 2 ...

    For MainType `ISCC`:

        MainTypes `DATA` and `INSTANCE` are mandatory for ISCC-CODEs, all others are
        optional. Length means the composition of optional 64-bit units included
        in the ISCC composite.

        Examples:
            No optional units      -> 0000 -> 0
            CONTENT                -> 0001 -> 1
            SEMANTIC               -> 0010 -> 2
            SEMANTIC, CONTENT      -> 0011 -> 3
            META                   -> 0100 -> 4
            META, CONTENT          -> 0101 -> 5
            ...

    For MainType `ID`:

        Lengths means number the number of bits for the body including the counter
        Length is encoded as number of bytes of the counter (64-bit body is implicit)
        Examples:
            64 -> 0 (No counter)
            72 -> 1 (One byte counter)
            80 -> 2 (Two byte counter)
            ...

    :param MainType mtype: The MainType for which to encode the length value.
    :param Length length: The length expressed according to the semantics of the type
    :return: The length value encoded as integer for use with write_header.
    :rtype: int
    """

    error = f"Invalid length {length} for MainType {mtype}"
    # standard case (length field denotes number of 32-bit chunks, 0 being 32-bits)
    if mtype in (MT.META, MT.SEMANTIC, MT.CONTENT, MT.DATA, MT.INSTANCE, MT.FLAKE):
        if length >= 32 and not length % 32:
            return (length // 32) - 1
        raise ValueError(error)
    # flag type encoding of included components (pass through as encoded out-of-band)
    elif mtype == MT.ISCC:
        if 0 <= length <= 7:
            return length
        raise ValueError(error)
    # counter byte length encoding
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

    Decodes a raw header integer value in to its semantically meaningfull value (e.g.
    number of bits)
    """
    if mtype in (MT.META, MT.SEMANTIC, MT.CONTENT, MT.DATA, MT.INSTANCE, MT.FLAKE):
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


def encode_base64(data):
    # type: (bytes) -> str
    """
    Standard RFC4648 base64url encoding without padding.
    """
    code = urlsafe_b64encode(data).decode("ascii")
    return code.rstrip("=")


def decode_base64(code):
    # type: (str) -> bytes
    """
    Standard RFC4648 base64url decoding without padding.
    """
    padding = 4 - (len(code) % 4)
    string = code + ("=" * padding)
    return urlsafe_b64decode(string)


def encode_base32hex(data):
    # type: (bytes) ->  str
    """
    RFC4648 Base32hex encoding without padding

    see: https://tools.ietf.org/html/rfc4648#page-10
    """
    b32 = encode_base32(data)
    return b32.translate(b32_to_hex)


def decode_base32hex(code):
    # type: (str) -> bytes
    """
    RFC4648 Base32hex decoding without padding

    see: https://tools.ietf.org/html/rfc4648#page-10
    """
    # Make sure we use upper-case version for translation
    b32 = code.upper().translate(hex_to_b32)
    return decode_base32(b32)


def iscc_decompose(iscc_code):
    # type: (str) -> List[str]
    """
    Decompose a normalized ISCC-CODE or any valid ISCC sequence into a list of ISCC-UNITS.

    A valid ISCC sequence is a string concatenation of ISCC-UNITS optionally seperated
    by a hyphen.
    """
    iscc_code = iscc_clean(iscc_code)
    components = []

    raw_code = decode_base32(iscc_code)
    while raw_code:
        mt, st, vs, ln, body = decode_header(raw_code)
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


def iscc_normalize(iscc_code):
    # type: (str) -> str
    """
    Normalize an ISCC to its canonical form.

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
        >>> iscc_core.iscc_normalize("GAAW2PRCRS5LNVZV-IAAUVACQKXE3V44W")
        'ISCC:KUAG2PRCRS5LNVZVJKAFAVOJXLZZM'

        ```

    :param str iscc_code: Any valid ISCC string
    :return: Normalized ISCC
    :rtype: str
    """
    from iscc_core.iscc_code import gen_iscc_code_v0

    decoders = {
        MULTIBASE.base16.value: bytes.fromhex,  # f
        MULTIBASE.base32.value: decode_base32,  # b
        MULTIBASE.base32hex.value: decode_base32hex,  # v
        MULTIBASE.base58btc.value: base58.b58decode,  # z
        MULTIBASE.base64url.value: decode_base64,  # u
    }

    # Transcode to base32 if <multibase><multicodec> encoded
    multibase_prefix = iscc_code[0]
    if multibase_prefix in decoders.keys():
        decoder = decoders[multibase_prefix]
        decoded = decoder(iscc_code[1:])
        if not decoded.startswith(MC_PREFIX):
            raise ValueError(f"Malformed multiformat codec: {decoded[:2]}")
        iscc_code = encode_base32(decoded[2:])
    else:
        prefix = iscc_code.upper().replace("ISCC:", "")[:2]
        if prefix not in PREFIXES:
            raise ValueError(f"ISCC starts with invalid prefix {prefix}")

    decomposed = iscc_decompose(iscc_code)
    recomposed = gen_iscc_code_v0(decomposed)["iscc"] if len(decomposed) >= 2 else decomposed[0]
    return f"ISCC:{recomposed}" if not recomposed.startswith("ISCC:") else recomposed


########################################################################################
# Convenience functions and classes                                                    #
########################################################################################


def iscc_decode(iscc):
    # type: (str) -> IsccTuple
    """
    Decode ISCC to an IsccTuple

    :param str iscc: ISCC string
    :return: ISCC decoded to a tuple
    :rtype: IsccTuple
    """
    iscc = iscc_clean(iscc_normalize(iscc))
    data = decode_base32(iscc)
    return decode_header(data)


def iscc_explain(iscc):
    # type: (str) -> str
    """
    Convert ISCC to a human-readable representation

    :param str iscc: ISCC string
    :return: Human-readable representation of ISCC
    :rtype: str
    """
    tid = iscc_type_id(iscc)
    fields = iscc_decode(iscc)
    if fields[0] == MT.ID:
        counter_bytes = fields[-1][8:]
        if counter_bytes:
            counter = uvarint.decode(counter_bytes)
            hex_hash = fields[-1][:8].hex()
            return f"{tid}-{hex_hash}-{counter.integer}"
    hex_hash = fields[-1].hex()
    return f"{tid}-{hex_hash}"


def iscc_type_id(iscc):
    # type: (str) -> str
    """
    Extract and convert ISCC HEADER to a readable Type-ID string.

    Type-ids can be used as names in databases to index ISCC-UNITs seperatly.

    :param str iscc: ISCC string
    :return: Unique Type-ID string
    :rtype: str
    """
    fields = iscc_decode(iscc)
    mtype = MT(fields[0])
    stype = SUBTYPE_MAP[fields[0]](fields[1])

    if mtype == MT.ISCC:
        mtypes = decode_units(fields[3])
        length = "".join([t.name[0] for t in mtypes]) + "DI"
    else:
        length = decode_length(fields[0], fields[3])

    version = VS(fields[2])

    return f"{mtype.name}-{stype.name}-{version.name}-{length}"


def iscc_validate(iscc, strict=True):
    # type: (str, bool) -> bool
    """
    Validate that a given string is a *strictly well-formed* ISCC.

    A *strictly well-formed* ISCC is:

    - an ISCC-CODE or ISCC-UNIT
    - encoded with base32 upper without padding
    - has a valid combination of header values
    - is represented in its canonical form

    :param str iscc: ISCC string
    :param bool strict: Raise an exeption if validation fails (default True)
    :return: True if sting is valid else false. (raises ValueError in strict mode)
    :rtype: bool
    """

    # Basic regex validation
    match = CANONICAL_REGEX.match(iscc)
    if not match:
        if strict:
            raise ValueError("ISCC string does not match ^ISCC:[A-Z2-7]{10,68}$")
        else:
            return False

    # Base32 encoding test
    try:
        decode_base32(iscc.split(":")[1])
    except Exception as e:
        if strict:
            raise ValueError(e)
        else:
            return False

    cleaned = iscc_clean(iscc)

    # Prefix test
    prefix = cleaned[:2]
    if prefix not in PREFIXES:
        if strict:
            raise ValueError(f"Header starts with invalid sequence {prefix}")
        else:
            return False

    # Version test
    m, s, v, l, t = decode_header(decode_base32(cleaned))
    if v != 0:
        if strict:
            raise ValueError(f"Unknown version {v} in version header")
        else:
            return False

    # Length test
    expected_nbyptes = decode_length(m, l).value // 8
    actual_nbyptes = len(t)
    if expected_nbyptes != actual_nbyptes:
        if strict:
            raise ValueError(f"Header expects {expected_nbyptes} but got {actual_nbyptes} bytes")
        else:
            return False

    return True


def iscc_clean(iscc):
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
