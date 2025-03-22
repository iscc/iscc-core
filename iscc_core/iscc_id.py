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


####################################################################################################
# ISCC-IDv1 - Timestamp/Server-ID based ISCC-ID                                                    #
####################################################################################################


def gen_iscc_id_v1(timestamp, server_id, realm_id=0):
    # type: (int, int, int) -> dict
    """
    Generate an ISCC-IDv1 from a timestamp and a server-id with algorithm v1.

    The ISCC-IDv1 is a 64-bit identifier constructed from a timestamp and a server-id
    where the first 52 bits denote the UTC time in microseconds since UNIX timestamp epoch and the
    last 12 bits denote the ID of the timestamping server. With 52-bit timestamps a single server
    can issue up to 1 Million timestamps per second until the year 2112. The server-id suffix
    allows for a deployment of up to 4096 timestamp servers and ensures that timestampes are
    distributed, globaly unique and support total ordering in integer and base32hex representations.
    With 52-bits for the timestamp and 12-bits for server-ids the system supports a theoretical
    maximum of ~4 billion unique timestamps per second. In the unlikely case that the ID-Space
    becomes to crowded we can further extend it by intrducing REALMs via additional ISCC-HEADER
    SUBTYPEs.

    ISCC-IDv1 are minted and digitally signed by authoritative ISCC Notary Servers organized in a
    federated system. The validity of an ISCC-IDv1 depends on the correct minting procedure as
    defined by the `ISCC Notary Protocol` (IEP-0016).

    Timestamp minting requirements:
        - A time source of at least microsecond precision
        - Yielding strictly monotonic (always increasing) integer timestamps
        - Measures to prevent front-running of actual time

    Server-ID `0` is reserved for sandbox/testing purposes. As such an ISCC-IDv1 with Server-ID 0:
        - makes no promises about uniqueness
        - is not authoritative
        - shall not be relied upon in production systems

    The ISCC-IDv1 has the following format:

    - Scheme Prefix: `ISCC:`
    - Base32-Encoded concatenation of:
      - 16-bit header: Concatenation of the nibbles:
        - MAINTYPE = "0110"  # ISCC-ID
        - SUBTYPE  = "0000"  # REALM
        - VERSION  = "0001"  # V1
        - LENGTH   = "0001"  # 64-bit
      - 52-bit timestamp: Current microseconds since 1970-01-01T00:00:00Z
      - 12-bit server-id: The Time Server ID

    :param int timestamp: Microseconds since 1970-01-01T00:00:00Z.
    :param int server_id: Server-ID that minted the ISCC-ID.
    :param int realm_id: Realm that minted the ISCC-ID.
    :return: ISCC object with an ISCC-ID (key: `iscc`)
    :rtype: dict
    """

    if timestamp >= 2**52:  # Ensure timestamp fits in 52 bits
        raise ValueError("Timestamp overflow")

    # Shift timestamp left by 12 bits and combine with server ID
    body = (timestamp << 12) | server_id

    # Pack the 64-bit body into 8 bytes
    digest = body.to_bytes(8, byteorder="big")

    iscc_id = ic.encode_component(
        mtype=ic.MT.ID,
        stype=realm_id,
        version=ic.VS.V1,
        bit_length=64,
        digest=digest,
    )
    iscc = "ISCC:" + iscc_id
    return dict(iscc=iscc)
