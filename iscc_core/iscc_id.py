# -*- coding: utf-8 -*-
"""*A globally unique, owned, and short identifier for digital assets.*

The **ISCC-ID** is a 64-bit identifier constructed from a timestamp and a server-ID:
- First 52 bits: UTC time in microseconds since UNIX epoch (1970-01-01T00:00:00Z)
- Last 12 bits: ID of the timestamping server (0-4095)

With this structure:
- A single server can issue up to 1 million timestamps per second until the year 2112
- The system supports up to 4096 timestamp servers (IDs 0-4095)
- Timestamps are globally unique and support total ordering in both integer and base32hex forms
- The theoretical maximum throughput is ~4 billion unique timestamps per second

ISCC-IDs are minted and digitally signed by authoritative ISCC Notary Servers in a
federated system. A valid ISCC-ID is guaranteed to be bound to an owner represented by a
cryptographic public key. The rules by which ISCC-IDs can be verified and resolved are defined
by the `ISCC Notary Protocol` (IEP-0011 - TBD).

The module also contains legacy support for the older v0 ISCC-ID format that was based on
blockchain wallet addresses and similarity-hashes of ISCC-CODE units.
"""

from hashlib import sha256
from typing import Optional
import uvarint
import iscc_core as ic

__all__ = [
    "gen_iscc_id",
    "gen_iscc_id_v0",
    "gen_iscc_id_v1",
    "iscc_id_incr",
    "iscc_id_incr_v0",
    "alg_simhash_from_iscc_id",
]


def gen_iscc_id(timestamp, server_id, realm_id=0):
    # type: (int, int, int) -> dict
    """
    Generate  ISCC-ID from ISCC-CODE with the latest standard algorithm.

    :param int timestamp: Microseconds since 1970-01-01T00:00:00Z (must be < 2^52)
    :param int server_id: Server-ID that minted the ISCC-ID (0-4095)
    :param int realm_id: Realm ID for the ISCC-ID (default: 0)
    :return: Dictionary with the ISCC-ID under the key 'iscc'
    :rtype: dict
    :raises ValueError: If an input is invalid
    """
    return gen_iscc_id_v1(timestamp, server_id, realm_id)


####################################################################################################
# ISCC-IDv1 - Timestamp/Server-ID based ISCC-ID                                                    #
####################################################################################################


def gen_iscc_id_v1(timestamp, server_id, realm_id=0):
    # type: (int, int, int) -> dict
    """
    Generate an ISCC-IDv1 from a timestamp and a server-id with algorithm v1.

    The ISCC-IDv1 is a 64-bit identifier constructed from a timestamp and a server-id:
    - First 52 bits: UTC time in microseconds since UNIX epoch (1970-01-01T00:00:00Z)
    - Last 12 bits: ID of the timestamping server (0-4095)

    With this structure:
    - A single server can issue up to 1 million timestamps per second until the year 2112
    - The system supports up to 4096 timestamp servers (IDs 0-4095)
    - Timestamps are globally unique and support total ordering in both integer and base32hex forms
    - The theoretical maximum throughput is ~4 billion unique timestamps per second

    If the ID space becomes crowded, it can be extended by introducing additional REALMS via
    ISCC-HEADER SUBTYPEs.

    ## Minting Authority

    ISCC-IDv1s are minted and digitally signed by authoritative ISCC Notary Servers in a
    federated system. A valid ISCC-IDv1 is guanteed to be bound to an owner represented by a
    cryptographic public key. The rules by which ISCC-IDv1 can be verified and resolved are defined
    by the `ISCC Notary Protocol` (IEP-0011 - TBD).

    ## Timestamp Requirements

    Timestamp minting requires:
    - A time source with at least microsecond precision
    - Strictly monotonic (always increasing) integer timestamps
    - Measures to prevent front-running of actual time

    ## Server ID Reservations

    Server-ID `0` is reserved for sandbox/testing purposes. An ISCC-IDv1 with Server-ID 0:
    - Makes no promises about uniqueness
    - Is not authoritative
    - Should not be used in production systems

    ## Technical Format

    The ISCC-IDv1 has the following format:
    - Scheme Prefix: `ISCC:`
    - Base32-Encoded concatenation of:
      - 16-bit header:
        - MAINTYPE = "0110" (ISCC-ID)
        - SUBTYPE  = "0000" (REALM, configurable via realm_id)
        - VERSION  = "0001" (V1)
        - LENGTH   = "0001" (64-bit)
      - 52-bit timestamp: Microseconds since 1970-01-01T00:00:00Z
      - 12-bit server-id: The Time Server ID (0-4095)

    :param int timestamp: Microseconds since 1970-01-01T00:00:00Z (must be < 2^52)
    :param int server_id: Server-ID that minted the ISCC-ID (0-4095)
    :param int realm_id: Realm ID for the ISCC-ID (default: 0)
    :return: Dictionary with the ISCC-ID under the key 'iscc'
    :rtype: dict
    :raises ValueError: If an input is invalid
    """

    if timestamp >= 2**52:  # Ensure timestamp fits in 52 bits
        raise ValueError("Timestamp overflow")

    if server_id >= 2**12:  # Ensure server-id fits in 12 bits
        raise ValueError("Server-ID overflow")

    if realm_id != 0:  # For the beginning we only support REALM 0
        raise ValueError("Realm-ID overflow")

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


####################################################################################################
# ISCC-IDv0 - Legacy experimental ISCC-IDv0 keept for backward compatibility                       #
####################################################################################################


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
