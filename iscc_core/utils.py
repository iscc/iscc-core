# -*- coding: utf-8 -*-
import io
import json
from hashlib import sha256
from typing import Generator, Sequence, Tuple, Any
import uvarint
from bitarray import bitarray
from bitarray.util import count_xor
from blake3 import blake3
import iscc_core as ic
import jcs
from iscc_core.constants import Stream

__all__ = [
    "iscc_nph_similarity",
    "iscc_nph_distance",
    "json_canonical",
    "cidv1_hex",
    "cidv1_to_token_id",
    "cidv1_from_token_id",
    "sliding_window",
    "iscc_similarity",
    "iscc_compare",
    "iscc_distance",
    "iscc_distance_bytes",
    "multi_hash_blake3",
]


def iscc_nph_similarity(a, b):
    # type: (bytes, bytes) -> dict
    """
    Calculate Normalized Prefix Hamming Similarity (NPHS) between two byte strings.

    NPHS is defined as 1.0 minus the Normalized Prefix Hamming Distance (NPHD).
    It represents the fraction of matching bits within the common prefix.

    :param a: First byte string
    :param b: Second byte string
    :return: Dictionary with NPHS score and common prefix length
             {"similarity": float, "common_prefix_bits": int}
    """
    common_bytes = min(len(a), len(b))
    common_bits = common_bytes * 8
    if common_bits == 0:
        return {
            "similarity": 1.0 if (len(a) == 0 and len(b) == 0) else 0.0,
            "common_prefix_bits": 0,
        }
    ba, bb = bitarray(), bitarray()
    ba.frombytes(a[:common_bytes])
    bb.frombytes(b[:common_bytes])
    hd = count_xor(ba, bb)
    return {"similarity": 1.0 - (hd / common_bits), "common_prefix_bits": common_bits}


def iscc_nph_distance(a, b):
    # type: (bytes, bytes) -> dict
    """
    Calculate Normalized Prefix Hamming Distance (NPHD) between two byte strings.

    NPHD is defined as the Hamming distance of their common prefix, normalized by
    the length of that common prefix in bits.

    :param a: First byte string
    :param b: Second byte string
    :return: Dictionary with NPHD score and common prefix length
             {"distance": float, "common_prefix_bits": int}
    """
    common_bytes = min(len(a), len(b))
    common_bits = common_bytes * 8
    if common_bits == 0:
        return {"distance": 0.0 if (len(a) == 0 and len(b) == 0) else 1.0, "common_prefix_bits": 0}
    ba, bb = bitarray(), bitarray()
    ba.frombytes(a[:common_bytes])
    bb.frombytes(b[:common_bytes])
    hd = count_xor(ba, bb)
    return {"distance": hd / common_bits, "common_prefix_bits": common_bits}


def json_canonical(obj):
    # type: (Any) -> bytes
    """
    Canonical, deterministic serialization of ISCC metadata.

    We serialize ISCC metadata in a deterministic/reproducible manner by using
    [JCS (RFC 8785)](https://datatracker.ietf.org/doc/html/rfc8785) canonicalization.
    """
    ser = jcs.canonicalize(obj)
    des = json.loads(ser)
    if des != obj:
        raise ValueError(f"Not canonicalizable {obj} round-trips to {des}")
    return ser


def cidv1_hex(stream):
    # type: (Union[Stream, bytes]) -> str
    """
    Create a [IPFS CIDv1](https://specs.ipld.io/block-layer/CID.html#cids-version-1) hash for ISCC
    metadata in `base16` (hexadecimal) representation.

    Learn more about IPFS CIDv1 at [ProtoSchool](https://proto.school/anatomy-of-a-cid)

    We use the default `CIDv1` with `sha1-256` and chunksize `262144` as hashing
    algorithm for ISCC metadata.

    !!! attention
        We use the `base16` (hexadecimal) representation for the CIDv1. This gives as
        stable, fixed-length CIDv1 header-prefix and allows us to use the CIDv1 as an
        [ERC-721](https://eips.ethereum.org/EIPS/eip-721)/[ERC-1155](https://eips.ethereum.org/EIPS/eip-1155)
        `uint256` Token-ID while also supporting ID-substitution for the metadata URI.

        For details see discussion at
        [OpenZeppelin Forum](https://forum.openzeppelin.com/t/how-to-erc-1155-id-substitution-for-token-uri/3312/14)


    !!! example
        ```python
        >>> import io
        >>> import iscc_core as ic
        >>> ic.cidv1_hex(io.BytesIO(b'hello world'))
        'f01551220b94d27b9934d3e08a52e52d7da7dabfac484efe37a5380ee9088f7ace2efcde9'

        ```

        The result might not look like a valid IPFS CIDv1, but it actually is:
        https://ipfs.io/ipfs/f01551220b94d27b9934d3e08a52e52d7da7dabfac484efe37a5380ee9088f7ace2efcde9

        With IPFS v0.11.0 this equals to:
        ```bash
        $ipfs add --cid-version=1 <myfile>
        $ipfs cid format -b=base16 bafkreifzjut3te2nhyekklss27nh3k72ysco7y32koao5eei66wof36n5e
        f01551220b94d27b9934d3e08a52e52d7da7dabfac484efe37a5380ee9088f7ace2efcde9
        ```

        When using `cidv1_to_token_id` for this hash you get an `uint256` that can be converted
        to a hex representation within a Smart Contract. The hex-representation can then be
        used for ID-Substitution. Use `ipfs://f01551220{id}` as template for the Metadata-URI.

    :param Stream stream: Data to be hashed (currently max 262144 bytes supported)
    :return: A valid IPFS CIDv1 that can be used as token-id and metadata-uri
    :rtype: str
    """

    if isinstance(stream, bytes):
        stream = io.BytesIO(stream)

    ipfs_max_size = 262144
    data = stream.read(ipfs_max_size)

    # fail if we have more data than ipfs_max_size
    if stream.read(1):
        raise ValueError(
            f"Data exceeds current max size {ipfs_max_size} for ipfs_hash: {len(data)}"
        )

    digest = sha256(data).digest()
    multibase_prefix = "f"
    multicodec_cidv1 = b"\x01"
    multicodec_content_type = b"\x55"  # raw
    multicodec_mutihash_type = b"\x12"  # sha2-256
    multicodec_mutihash_len = uvarint.encode(32)  # 28 byte length (varint encoded 0x1c)

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


def cidv1_to_token_id(cidv1):
    # type: (str) -> int
    """
    Convert default IPFS CIDv1 to an uint256 Token-ID.

    To save storage space in Smart Contracts and to securely link an NFT Token-ID to its associated
    metadata we can convert a CIDv1 to an uint256 Token-ID and vice versa.

    !!! example

        ```python
        >>> import io
        >>> import iscc_core as ic
        >>> ic.cidv1_to_token_id("f01551220b94d27b9934d3e08a52e52d7da7dabfac484efe37a5380ee9088f7ace2efcde9")
        83814198383102558219731078260892729932246618004265700685467928187377105751529

        ```

    :param str cidv1: An IPFS CIDv1 string base-16 (hex) encoded representation.
    :return int: An uint256 derived from the CIDv1
    """
    if not cidv1.startswith("f"):
        raise ValueError(f"Only base16 encoded CIDv1 supported. Got {cidv1}")
    nobase = cidv1[1:]
    decoded = bytes.fromhex(nobase)
    if not decoded.startswith(b"\x01\x55\x12\x20"):
        raise ValueError(f"Only sha2-256 with raw leaves supported. Got {decoded.hex()}")
    digest = decoded[4:]
    if not len(digest) == 32:
        raise ValueError(f"Illegal digest size {len(digest)} for sha2-256")
    return int.from_bytes(digest, "big", signed=False)


def cidv1_from_token_id(token_id):
    # type: (int) -> str
    """
    Convert Token-ID to default IPFS CIDv1 (reverse of `cidv1_to_token_id`).

    !!! example
        ```python
        >>> import io
        >>> import iscc_core as ic
        >>> ic.cidv1_from_token_id(83814198383102558219731078260892729932246618004265700685467928187377105751529)
        'f01551220b94d27b9934d3e08a52e52d7da7dabfac484efe37a5380ee9088f7ace2efcde9'

        ```

    :param token_id: An uint256 Token-ID derived from a CIDv1
    :return str: An IPFS CIDv1 string with default base32 encoding.
    """
    digest = b"\x01\x55\x12\x20" + int.to_bytes(token_id, length=32, byteorder="big", signed=False)
    return "f" + digest.hex()


def multi_hash_blake3(data):
    # type: (bytes) -> str
    """
    Create blake3 hash with multihash prefix.

    :param bytes data: Bytes to be hashed
    :return: Multihash prefixed 256-bit blake3 hash as hex string
    :rtype: str
    """
    return (b"\x1e\x20" + blake3(data).digest()).hex()


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


def iscc_compare(a, b):
    # type: (str, str) -> dict
    """
    Calculate separate hamming distances of compatible components of two ISCCs.
    For ISCC-IDv1, returns a simple match comparison result.

    :return: A dict with component distances or match result for ISCC-IDv1
    :rtype: dict
    """
    ac = [ic.Code(unit) for unit in ic.iscc_decompose(a)]
    bc = [ic.Code(unit) for unit in ic.iscc_decompose(b)]

    # Special handling for ISCC-IDv1
    for code in ac + bc:
        if code.maintype == ic.MT.ID and code.version == ic.VS.V1:
            return {"id_match": code.hash_bytes == code.hash_bytes}

    result = {}
    for ca in ac:
        for cb in bc:
            cat = (ca.maintype, ca.subtype, ca.version)
            cbt = (cb.maintype, cb.subtype, ca.version)
            if cat == cbt:
                if ca.maintype != ic.MT.INSTANCE:
                    result[ca.maintype.name.lower() + "_dist"] = iscc_distance_bytes(
                        ca.hash_bytes, cb.hash_bytes
                    )
                else:
                    result["instance_match"] = ca.hash_bytes == cb.hash_bytes
    return result


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
    :raise ValueError: If ISCC headers don´t match or for unsupported types
    """
    a, b = ic.iscc_clean(ic.iscc_normalize(a)), ic.iscc_clean(ic.iscc_normalize(b))
    a, b = ic.decode_base32(a), ic.decode_base32(b)
    a, b = ic.decode_header(a), ic.decode_header(b)

    # Check for ISCC-IDv1 which doesn't support similarity comparison
    if a[0] == ic.MT.ID and a[2] == ic.VS.V1:
        raise ValueError("Similarity comparison not supported for ISCC-IDv1")
    if b[0] == ic.MT.ID and b[2] == ic.VS.V1:
        raise ValueError("Similarity comparison not supported for ISCC-IDv1")

    if not a[:-1] == b[:-1]:
        raise ValueError(f"ISCC headers don´t match: {a}, {b}")
    return a[-1], b[-1]
