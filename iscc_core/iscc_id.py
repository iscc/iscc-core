# -*- coding: utf-8 -*-
"""*A decentralized, owned, and short identifier for digital assets.*

The **ISCC-ID** is generated from a similarity-hash of the units of an
**ISCC-CODE** together with a blockchain wallet address. Its SubType designates the blockchain
from which the **ISCC-ID** was minted. The similarity-hash is always at least 64-bits and
optionally suffixed with a [`uvarint`](https://github.com/multiformats/unsigned-varint) endcoded
`uniqueness counter`. The `uniqueness counter` is added and incremented only if the
mint colides with a pre-existing **ISCC-ID** minted from the same blockchain from a
different **ISCC-CODE** or from an identical **ISCC-CODE** registered by a different
signatory.
"""
from hashlib import sha256
from typing import Optional
import uvarint
import iscc_core as ic


__all__ = [
    "gen_iscc_id",
    "gen_iscc_id_v0",
    "iscc_id_incr",
    "iscc_id_incr_v0",
    "alg_simhash_from_iscc_id",
]


def gen_iscc_id(iscc_code, chain_id, wallet, uc=0):
    # type: (str, int, str, Optional[int]) -> dict
    """
    Generate  ISCC-ID from ISCC-CODE with the latest standard algorithm.

    :param str iscc_code: The ISCC-CODE from which to mint the ISCC-ID.
    :param int chain_id: Chain-ID of blockchain from which the ISCC-ID is minted.
    :param str wallet: The wallet address that signes the ISCC declaration
    :param int uc: Uniqueness counter of ISCC-ID.
    :return: ISCC object with an ISCC-ID
    :rtype: dict
    """
    return gen_iscc_id_v0(iscc_code, chain_id, wallet, uc)


def gen_iscc_id_v0(iscc_code, chain_id, wallet, uc=0):
    # type: (str, int, str, Optional[int]) -> dict
    """
    Generate an ISCC-ID from an ISCC-CODE with uniqueness counter 'uc' with
    algorithm v0.

    :param str iscc_code: The ISCC-CODE from which to mint the ISCC-ID.
    :param int chain_id: Chain-ID of blockchain from which the ISCC-ID is minted.
    :param str wallet: The wallet address that signes the ISCC declaration
    :param int uc: Uniqueness counter of ISCC-ID.
    :return: ISCC object with an ISCC-ID
    :rtype: dict
    """
    if chain_id not in list(ic.ST_ID):
        raise AssertionError("Unknown Chain-ID {}".format(chain_id))
    iscc_id_digest = soft_hash_iscc_id_v0(iscc_code, wallet, uc)
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


def soft_hash_iscc_id_v0(iscc_code, wallet, uc=0):
    # type: (str, str, int) -> bytes
    """
    Calculate ISCC-ID hash digest from ISCC-CODE with algorithm v0.

    Accepts an ISCC-CODE or any sequence of ISCC-UNITs.

    :param str iscc_code: ISCC-CODE
    :param str wallet: The wallet address that signes the ISCC declaration
    :param int uc: Uniqueness counter for ISCC-ID.
    :return: Digest for ISCC-ID without header but including uniqueness counter.
    :rtype: bytes
    """
    components = ic.iscc_decompose(iscc_code)
    decoded = [ic.decode_base32(c) for c in components]
    unpacked = [ic.decode_header(d) for d in decoded]

    digests = []

    if len(unpacked) == 1 and unpacked[0][0] == ic.MT.INSTANCE:
        # Special case if iscc_code is a singular Instance-Code
        digests.append(decoded[0][:1] + unpacked[0][-1][:7])
    else:
        for dec, unp in zip(decoded, unpacked):
            mt = unp[0]
            if mt == ic.MT.INSTANCE:
                continue
            if mt == ic.MT.ID:
                raise ValueError("Cannot create ISCC-ID from ISCC-ID")
            # first byte of header + first 7 bytes of body
            digests.append(dec[:1] + unp[-1][:7])

    iscc_id_digest = ic.alg_simhash(digests)

    # XOR with sha2-256 of wallet
    wallet_hash_digest = sha256(wallet.encode("ascii")).digest()[:8]
    iscc_id_xor_digest = bytes(a ^ b for (a, b) in zip(iscc_id_digest, wallet_hash_digest))

    if uc:
        iscc_id_xor_digest += uvarint.encode(uc)
    return iscc_id_xor_digest


def iscc_id_incr(iscc_id):
    # type: (str) -> str
    """
    Increment uniqueness counter of an ISCC-ID with latest standard algorithm.

    :param str iscc_id: Base32-encoded ISCC-ID.
    :return: Base32-encoded ISCC-ID with counter incremented by one.
    :rtype: str
    """
    return iscc_id_incr_v0(iscc_id)


def iscc_id_incr_v0(iscc_id):
    # type: (str) -> str
    """
    Increment uniqueness counter of an ISCC-ID with algorithm v0.

    :param str iscc_id: Base32-encoded ISCC-ID.
    :return: Base32-encoded ISCC-ID with counter incremented by one (without "ISCC:" prefix).
    :rtype: str
    """
    clean = ic.iscc_clean(iscc_id)
    code_digest = ic.decode_base32(clean)
    mt, st, vs, ln, data = ic.decode_header(code_digest)
    if mt != ic.MT.ID:
        raise AssertionError(f"MainType {mt} is not ISCC-ID")
    if st not in list(ic.ST_ID):
        raise AssertionError(f"Unsupported chain-id {st}")
    if vs != ic.VS.V0:
        raise AssertionError(f"Version {vs} is not v0")
    if len(data) == 8:
        data += uvarint.encode(1)
    else:
        counter = uvarint.decode(data[8:])
        suffix = uvarint.encode(counter.integer + 1)
        data = data[:8] + suffix

    iscc_id_len = len(data) * 8
    iscc_id = ic.encode_component(
        mtype=mt,
        stype=st,
        version=vs,
        bit_length=iscc_id_len,
        digest=data,
    )

    return iscc_id


def alg_simhash_from_iscc_id(iscc_id, wallet):
    # type: (str, str) -> str
    """
    Extract similarity preserving hex-encoded hash digest from ISCC-ID

    We need to un-xor the ISCC-ID hash digest with the wallet address hash to obtain the similarity
    preserving bytestring.
    """
    wallet_hash_digest = sha256(wallet.encode("ascii")).digest()[:8]
    cleaned = ic.iscc_clean(iscc_id)
    iscc_tuple = ic.iscc_decode(cleaned)
    iscc_id_xor_digest = iscc_tuple[4][:8]
    iscc_id_digest = bytes(a ^ b for (a, b) in zip(iscc_id_xor_digest, wallet_hash_digest))
    return iscc_id_digest.hex()
