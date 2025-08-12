# -*- coding: utf-8 -*-
import re
import enum
from typing import Tuple, Union

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
Meta = Union[dict, str]
FrameSig = Tuple[int]

b32_to_hex = str.maketrans("ABCDEFGHIJKLMNOPQRSTUVWXYZ234567", "0123456789ABCDEFGHIJKLMNOPQRSTUV")
hex_to_b32 = str.maketrans("0123456789ABCDEFGHIJKLMNOPQRSTUV", "ABCDEFGHIJKLMNOPQRSTUVWXYZ234567")


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
    | 5    | ISCC     | 0101 | Composite of two or more ISCC-UNITs with common header  |
    """

    META = 0
    SEMANTIC = 1
    CONTENT = 2
    DATA = 3
    INSTANCE = 4
    ISCC = 5
    ID = 6
    FLAKE = 7


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
    | 6    | NONE     | 0110 | Composite ISCC including Meta, Data and Instance-Code   |
    | 7    | WIDE     | 0111 | Composite ISCC with 128-bit Data- and Instance-Code     |
    """

    TEXT = 0
    IMAGE = 1
    AUDIO = 2
    VIDEO = 3
    MIXED = 4
    SUM = 5
    NONE = 6
    WIDE = 7


class ST_ID(enum.IntEnum):
    """
    ### ST_ID

    SubTypes for `MT.ID`

    | Uint | Symbol   | Bits | Purpose                                                 |
    |----- |:---------|------|---------------------------------------------------------|
    | 0    | PRIVATE  | 0000 | ISCC-ID minted via private repository (not unique)      |
    | 1    | BITCOIN  | 0001 | ISCC-ID minted via Bitcoin blockchain                   |
    | 2    | ETHEREUM | 0010 | ISCC-ID minted via Ethereum blockchain                  |
    | 3    | POLYGON  | 0011 | ISCC-ID minted via Polygon blockchain                   |
    """

    PRIVATE = 0
    BITCOIN = 1
    ETHEREUM = 2
    POLYGON = 3


class ST_ID_REALM(enum.IntEnum):
    """
    ### ST_ID_REALM

    SubTypes for `MT.ID` with Version V1 (Realm IDs)

    | Uint | Symbol   | Bits | Purpose                                                 |
    |----- |:---------|------|---------------------------------------------------------|
    | 0    | REALM_0  | 0000 | Test HUB network realm for ISCC-IDv1                   |
    | 1    | REALM_1  | 0001 | First operational HUB network realm for ISCC-IDv1      |
    """

    REALM_0 = 0  # Test HUB network
    REALM_1 = 1  # First operational realm


class VS(enum.IntEnum):
    """
    ## VS - Version

    Code Version

    | Uint | Symbol   | Bits | Purpose                                                 |
    |----- |:---------|------|---------------------------------------------------------|
    | 0    | V0       | 0000 | Initial Version of Code or Unit                         |
    | 1    | V1       | 0001 | Updated Version of Code or Unit                         |

    """

    V0 = 0
    V1 = 1


class LN(enum.IntEnum):
    """
    ## LN - Length

    Valid lengths for hash-digests.

    - L32 = 32
    - L64 = 64
    - L72 = 72
    - L80 = 80
    - L96 = 96
    - L128 = 128
    - L160 = 160
    - L192 = 192
    - L224 = 224
    - L256 = 256
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
    L320 = 320


class MULTIBASE(str, enum.Enum):
    """
    Supported Multibase encodings.

    - base16 -> f
    - base32 -> b
    - base32hex -> v
    - base58btc -> z
    - base64url -> u
    """

    base16 = "f"
    base32 = "b"
    base32hex = "v"
    base58btc = "z"
    base64url = "u"


#: Possible combinations of ISCC units for the first 3 units of MT.ISCC
UNITS = (
    tuple(),
    (MT.CONTENT,),
    (MT.SEMANTIC,),
    (
        MT.SEMANTIC,
        MT.CONTENT,
    ),
    (MT.META,),
    (MT.META, MT.CONTENT),
    (MT.META, MT.SEMANTIC),
    (MT.META, MT.SEMANTIC, MT.CONTENT),
)

#: Map MainTypes to SubTypes
SUBTYPE_MAP = {
    (MT.META, VS.V0): ST,
    (MT.SEMANTIC, VS.V0): ST_CC,
    (MT.CONTENT, VS.V0): ST_CC,
    (MT.DATA, VS.V0): ST,
    (MT.INSTANCE, VS.V0): ST,
    (MT.ISCC, VS.V0): ST_ISCC,
    (MT.ID, VS.V0): ST_ID,
    (MT.ID, VS.V1): ST_ID_REALM,
    (MT.FLAKE, VS.V0): ST,
}

#: Multicodec prefix code
MC_PREFIX: bytes = b"\xcc\x01"

# Valid 2-character ISCC prefixes (note: MA and ME are ambiguous between V0 and V1)
PREFIXES = [
    "AA",  # META-NONE
    "CA",  # SEMANTIC-TEXT
    "CE",  # SEMANTIC-IMAGE
    "CI",  # SEMANTIC-AUDIO
    "CM",  # SEMANTIC-VIDEO
    "CQ",  # SEMANTIC-MIXED
    "EA",  # CONTENT-TEXT
    "EE",  # CONTENT-IMAGE
    "EI",  # CONTENT-AUDIO
    "EM",  # CONTENT-VIDEO
    "EQ",  # CONTENT-MIXED
    "GA",  # DATA-NONE
    "IA",  # INSTANCE-NONE
    "KA",  # ISCC-TEXT
    "KE",  # ISCC-IMAGE
    "KI",  # ISCC-AUDIO
    "KM",  # ISCC-VIDEO
    "KQ",  # ISCC-MIXED
    "KU",  # ISCC-SUM
    "KY",  # ISCC-NONE
    "K4",  # ISCC-WIDE
    "MA",  # ID-PRIVATE-V0 / ID-REALM_0-V1 (ambiguous)
    "ME",  # ID-BITCOIN-V0 / ID-REALM_1-V1 (ambiguous)
    "MI",  # ID-ETHEREUM-V0
    "MM",  # ID-POLYGON-V0
    "OA",  # FLAKE-NONE
]

CANONICAL_REGEX = re.compile("^ISCC:[A-Z2-7]{10,68}$")
