# -*- coding: utf-8 -*-
"""*A decentralized short identifier for digital assets.*

The **ISCC-ID** is generated from a similarity-hash of the components of an
**ISCC-CODE**. Its SubType designates the blockchain from which the **ISCC-ID** was
minted. The similarity-hash is always at least 64-bits and optionally suffixed with a
[`uvarint`](https://github.com/multiformats/unsigned-varint) endcoded
`uniqueness counter`. The `uniqueness counter` is added and incremented only if the
mint colides with a pre-existing **ISCC-ID** minted from the same blockchain from a
different **ISCC-CODE** or from an identical **ISCC-CODE** registered by a different
signatory.
"""
import uvarint
import iscc_core as ic


def gen_iscc_id(chain, iscc_code, uc=0):
    # type: (int, str, int) -> dict
    """
    Generate  ISCC-ID from ISCC-CODE with the latest standard algorithm.

    :param int chain: Chain-ID of blockchain from which the ISCC-ID is minted.
    :param str iscc_code: The ISCC-CODE from which to mint the ISCC-ID.
    :param int uc: Uniqueness counter of ISCC-ID.
    :return: ISCC object with an ISCC-ID
    :rtype: dict
    """
    return gen_iscc_id_v0(chain, iscc_code, uc)


def gen_iscc_id_v0(chain_id, iscc_code, uc=0):
    # type: (int, str, int) -> dict
    """
    Generate an ISCC-ID from an ISCC-CODE with uniqueness counter 'uc' with
    algorithm v0.

    :param int chain_id: Chain-ID of blockchain from which the ISCC-ID is minted.
    :param str iscc_code: The ISCC-CODE from which to mint the ISCC-ID.
    :param int uc: Uniqueness counter for ISCC-ID.
    :return: ISCC object with an ISCC-ID
    :rtype: dict
    """
    if chain_id not in list(ic.ST_ID):
        raise AssertionError("Unregistered Chain-ID {}".format(chain_id))
    iscc_id_digest = soft_hash_iscc_id_v0(iscc_code, uc)
    iscc_id_len = len(iscc_id_digest) * 8
    iscc_id = ic.encode_component(
        mtype=ic.MT.ID,
        stype=chain_id,
        version=ic.VS.V0,
        bit_length=iscc_id_len,
        digest=iscc_id_digest,
    )
    iscc = "ISCC:" + iscc_id
    return dict(iscc=iscc)


def soft_hash_iscc_id_v0(iscc_code, uc=0):
    # type: (str, int) -> bytes
    """
    Calculate ISCC-ID hash digest from ISCC-CODE digest with algorithm v0.

    :param str iscc_code: ISCC-CODE
    :param int uc: Uniqueness counter for ISCC-ID.
    :return: Digest for ISCC-ID without header but including uniqueness counter.
    :rtype: bytes
    """
    components = ic.iscc_decompose(iscc_code)
    decoded = [ic.decode_base32(c) for c in components]
    unpacked = [ic.read_header(d) for d in decoded]

    digests = []

    if len(unpacked) == 1 and unpacked[0][0] == ic.MT.INSTANCE:
        # Special case if iscc_code is a singular Instance-Code
        digests.append(decoded[0][:1] + unpacked[0][-1][:7])
    else:
        digests = []
        for dec, unp in zip(decoded, unpacked):
            if unp[0] == ic.MT.INSTANCE:
                continue
            # first byte of header + first 7 bytes of body
            digests.append(dec[:1] + unp[-1][:7])

    iscc_id_digest = ic.similarity_hash(digests)

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
    code_digest = ic.decode_base32(iscc_id)
    mt, _, vs, _, _ = ic.read_header(code_digest)
    if mt != ic.MT.ID:
        raise AssertionError("MainType {} is not ISCC-ID".format(mt))
    if vs != ic.VS.V0:
        raise AssertionError("Version {} is not v0".format(vs))
    if len(code_digest) == 10:
        code_digest += uvarint.encode(1)
    else:
        decoded = uvarint.decode(code_digest[10:])
        code_digest = code_digest[:10] + uvarint.encode(decoded.integer + 1)
    return ic.encode_base32(code_digest)
