# -*- coding: utf-8 -*-
"""*A decentralized short identifier for digital assets.*

The **ISCC-ID** is generated from a similarity-hash of the components of an
**ISCC-CODE**. Its SubType designates the blockchain from which the **ISCC-ID** was
minted. The similarity-hash is always at least 64-bits and optionally suffixed with a
[`uvarint`](https://github.com/multiformats/unsigned-varint) endcoded
`uniqueness counter`. The `uniqueness counter` is added and incremented only if the
mint colides with a pre-existing **ISCC-ID minted** from the same blockchain from a
different **ISCC-CODE** or from an identical **ISCC-CODE** registered by a different
signatory.
"""
from iscc_core import simhash, codec, ST_ID
import uvarint


def gen_iscc_id(chain, iscc_code, uc=0):
    # type: (int, str, int) -> str
    """
    Generate an ISCC-ID from an ISCC-CODE with uniqueness counter 'uc' with latest
    standard algorithm.

    :param int chain: Chain-ID of blockchain from which the ISCC-ID is minted.
    :param str iscc_code: The ISCC-CODE from which to mint the ISCC-ID.
    :param int uc: Uniqueness counter of ISCC-ID.
    :return: ISCC-ID string.
    :rtype: str
    """
    return gen_iscc_id_v0(chain, iscc_code, uc)


def gen_iscc_id_v0(chain_id, iscc_code, uc=0):
    # type: (int, str, int) -> str
    """
    Generate an ISCC-ID from an ISCC-CODE with uniqueness counter 'uc' with
    algorithm v0.

    :param int chain_id: Chain-ID of blockchain from which the ISCC-ID is minted.
    :param str iscc_code: The ISCC-CODE from which to mint the ISCC-ID.
    :param int uc: Uniqueness counter for ISCC-ID.
    :return: ISCC-ID string.
    :rtype: str
    """
    assert chain_id in list(codec.ST_ID), "Unregistered Chain-ID {}".format(chain_id)
    digest = codec.decode_base32(iscc_code)
    iscc_id_digest = soft_hash_iscc_id_v0(digest, uc)
    iscc_id_len = len(iscc_id_digest) * 8
    iscc_id = codec.encode_component(
        mtype=codec.MT.ID,
        stype=chain_id,
        version=codec.VS.V0,
        length=iscc_id_len,
        digest=iscc_id_digest,
    )
    return iscc_id


def soft_hash_iscc_id_v0(digest, uc=0):
    # type: (bytes, int) -> bytes
    """
    Calculate ISCC-ID hash digest from ISCC-CODE digest with algorithm v0.

    :param bytes digest: Byte-Digest of ISCC-CODE
    :param int uc: Uniqueness counter for ISCC-ID.
    :return: Digest for ISCC-ID without header but including uniqueness counter.
    :rtype: bytes
    """
    components = codec.decompose(digest)
    digests = [
        c.header_bytes[:1] + c.hash_bytes[:7]
        for c in components
        if c.maintype != codec.MT.INSTANCE
    ]
    iscc_id_digest = simhash.similarity_hash(digests)
    if uc:
        iscc_id_digest += uvarint.encode(uc)
    return iscc_id_digest


def incr_iscc_id(iscc_id):
    # type: (str) -> str
    """
    Increment uniqueness counter of an ISCC-ID with latest standard algorithm.

    :param str iscc_id: Base32-encoded ISCC-ID.
    :return: Base32-encoded ISCC-ID with counter incremented by one.
    :rtype: str
    """
    return incr_iscc_id_v0(iscc_id)


def incr_iscc_id_v0(iscc_id):
    # type: (str) -> str
    """
    Increment uniqueness counter of an ISCC-ID with algorithm v0.

    :param str iscc_id: Base32-encoded ISCC-ID.
    :return: Base32-encoded ISCC-ID with counter incremented by one.
    :rtype: str
    """
    code_digest = codec.decode_base32(iscc_id)
    mt, st, vs, l, digest = codec.read_header(code_digest)
    assert mt == codec.MT.ID, "MainType {} is not ISCC-ID".format(mt)
    assert vs == codec.VS.V0, "Version {} is not v0".format(vs)
    if len(code_digest) == 10:
        code_digest += uvarint.encode(1)
    else:
        decoded = uvarint.decode(code_digest[10:])
        code_digest = code_digest[:10] + uvarint.encode(decoded.integer)
    return codec.encode_base32(code_digest)