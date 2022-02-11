# -*- coding: utf-8 -*-
from hashlib import sha3_224
from typing import Union, Dict, List, Generator, Sequence, Tuple
import uvarint
from bitarray import bitarray
from bitarray.util import count_xor
import iscc_core as ic
import jcs
from iscc_core.constants import Stream


__all__ = [
    "json_canonical",
    "ipfs_hash",
    "sliding_window",
    "iscc_similarity",
    "iscc_distance",
    "iscc_distance_bytes",
]


def json_canonical(obj):
    # type: (Union[Dict, List]) -> bytes
    """
    Canonical, deterministic serialization of ISCC metadata.

    We serialize ISCC metadata in a deterministic/reproducible manner by using
    [JCS (RFC 8785)](https://datatracker.ietf.org/doc/html/rfc8785) canonicalization.
    """
    return jcs.canonicalize(obj)


def ipfs_hash(stream):
    # type: (Stream) -> str
    """
    Create an [IPFS](https://ipfs.io) hash for ISCC metadata.

    We use a specialized `base16` encoded `CIDv1` with `sha3-224` and chunksize
    `1048576` as hashing algorithm for ISCC metadata.

    !!! example
        With IPFS v0.11.0 this equals to:
        ```bash
        $ipfs add --cid-version=1 --chunker=size-1048576 --hash=sha3-224 <myfile>
        <my-cid>
        $ipfs cid format -b=base16 <my-cid>
        ```

    !!! note
        The rationale for this trickery is that we want to be able to use an IPFS hash as an
        [ERC-721](https://eips.ethereum.org/EIPS/eip-721)/[ERC-1155](https://eips.ethereum.org/EIPS/eip-1155) `uint256 _tokenID` and
        also support ID substitution for the metadata URI. For details see discussion at
        [OpenZeppelin Forum](https://forum.openzeppelin.com/t/how-to-erc-1155-id-substitution-for-token-uri/3312/14)

    Learn more about IPFS CIDv1 at [ProtoSchool](https://proto.school/anatomy-of-a-cid)

    :param Stream stream: Data to be hashed (currently max 1048576)
    :return: A valid IPFS CIDv1 that can be used as token-id and metadata-uri
    :rtype: str
    """

    ipfs_max_size = 1048576
    data = stream.read(ipfs_max_size)

    # fail if we have more data than ipfs_max_size
    if stream.read(1):
        raise ValueError(
            f"Data exceeds current max size {ipfs_max_size} for ipfs_hash: {len(data)}"
        )

    digest = sha3_224(data).digest()
    multibase_prefix = "f"
    multicodec_cidv1 = b"\x01"
    multicodec_content_type = b"\x55"  # raw
    multicodec_mutihash_type = b"\x17"  # sha3-224
    multicodec_mutihash_len = uvarint.encode(28)  # 28 byte length (varint encoded 0x1c)

    cid_v1_digest = b"".join(
        (
            multicodec_cidv1,
            multicodec_content_type,
            multicodec_mutihash_type,
            multicodec_mutihash_len,
            digest,
        )
    )

    cid_v1 = multibase_prefix + cid_v1_digest.hex()
    return cid_v1


def sliding_window(seq, width):
    # type: (Sequence, int) -> Generator
    """
    Generate a sequence of equal "width" slices each advancing by one elemnt.

    All types that have a length and can be sliced are supported (list, tuple, str ...).
    The result type matches the type of the input sequence.
    Fragment slices smaller than the width at the end of the sequence are not produced.
    If "witdh" is smaller than the input sequence than one element will be returned that
    is shorter than the requested width.

    :param Sequence seq: Sequence of values to slide over
    :param int width: Width of sliding window in number of items
    :returns: A generator of window sized items
    :rtype: Generator
    """
    if width < 2:
        raise AssertionError("Sliding window width must be 2 or bigger.")
    idx = range(max(len(seq) - width + 1, 1))
    return (seq[i : i + width] for i in idx)


def iscc_similarity(a, b):
    # type: (str, str) -> int
    """
    Calculate similarity of ISCC codes as a percentage value (0-100).

    MainType, SubType, Version and Length of the codes must be the same.

    :param a: ISCC a
    :param b: ISCC b
    :return: Similarity of ISCC a and b in percent (based on hamming distance)
    :rtype: int
    """
    a, b = iscc_pair_unpack(a, b)
    hdist = iscc_distance_bytes(a, b)
    nbits = len(a) * 8
    sim = int(((nbits - hdist) / nbits) * 100)
    return sim


def iscc_distance(a, b):
    # type: (str, str) -> int
    """
    Calculate hamming distance of ISCC codes.

    MainType, SubType, Version and Length of the codes must be the same.

    :param a: ISCC a
    :param b: ISCC b
    :return: Hamming distanced in number of bits.
    :rtype: int
    """
    a, b = iscc_pair_unpack(a, b)
    return iscc_distance_bytes(a, b)


def iscc_distance_bytes(a, b):
    # type: (bytes, bytes) -> int
    """
    Calculate hamming distance for binary hash digests of equal length.

    :param bytes a: binary hash digest
    :param bytes b: binary hash digest
    :return: Hamming distance in number of bits.
    :rtype: int
    """
    if len(a) != len(b):
        raise AssertionError(f"Hash diggest of unequal length: {len(a)} vs {len(b)}")
    ba, bb = bitarray(), bitarray()
    ba.frombytes(a)
    bb.frombytes(b)
    return count_xor(ba, bb)


def iscc_pair_unpack(a, b):
    # type: (str, str) -> Tuple[bytes, bytes]
    """
    Unpack two ISCC codes and return their body hash digests if their headers match.

    Headers match if their MainType, SubType, and Version are identical.

    :param a: ISCC a
    :param b: ISCC b
    :return: Tuple with hash digests of a and b
    :rtype: Tuple[bytes, bytes]
    :raise ValueError: If ISCC headers don´t match
    """
    a, b = ic.iscc_clean(ic.iscc_normalize(a)), ic.iscc_clean(ic.iscc_normalize(b))
    a, b = ic.decode_base32(a), ic.decode_base32(b)
    a, b = ic.read_header(a), ic.read_header(b)
    if not a[:-1] == b[:-1]:
        raise ValueError(f"ISCC headers don´t match: {a}, {b}")
    return a[-1], b[-1]
