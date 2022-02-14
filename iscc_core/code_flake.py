# -*- coding: utf-8 -*-
"""*A unique identifier composed of an 48-bit timestamp and 16 to 208 bit randomness.*

!!! example
    ```ISCC:OAAQC7XVNNC5FM4U```


The ISCC Flake-Code is a surogate identifier for distributes ID generation. The 64-bit version
can be used as efficient suragate key in database systems. It has guaranteed uniqueness if
generated from a singele process and is time sortable in integer and base32hex representation.
The 128-bit version is a K-sortable globally unique identifier for use in distributed systems and
isc compatible with UUID.
"""
import os
import time
from collections import Counter
from datetime import datetime
from typing import Optional
import iscc_core as ic


__all__ = [
    "gen_flake_code",
    "gen_flake_code_v0",
    "hash_flake_v0",
    "flake_to_iso8601",
]

_COUNTER = Counter()


def gen_flake_code(bits=ic.core_opts.flake_bits):
    # type: (int) -> dict
    """
    Create an ISCC Flake-Code with the latest standard algorithm

    :param int bits: Target bit-length of generated Flake-Code
    :return: ISCC object with Flake-Code
    :rtype: dict
    """
    return gen_flake_code_v0(bits=bits)


def gen_flake_code_v0(bits=ic.core_opts.flake_bits):
    """
    Create an ISCC Flake-Code with the latest algorithm v0

    :param int bits: Target bit-length of generated Flake-Code
    :return: ISCC object with Flake-Code
    :rtype: dict
    """

    digest = hash_flake_v0(bits=bits)
    flake_code = ic.encode_component(
        mtype=ic.MT.FLAKE, stype=ic.ST.NONE, version=ic.VS.V0, bit_length=bits, digest=digest
    )
    iscc = "ISCC:" + flake_code
    return {"iscc": iscc}


def hash_flake_v0(ts=None, bits=ic.core_opts.flake_bits):
    # type: (Optional[float], int) -> bytes
    """
    Generate time and randomness based Flake-Hash

    :param Optional[float] ts: Unix timestamp (defaults to current time)
    :param int bits: Bit-length resulting Flake-Code (multiple of 32)
    :return: Flake-Hash digest
    :rtype: bytes
    """
    if not 64 <= bits <= 256:
        raise ValueError(f"{bits} bits for flake outside 64 - 256 bits")
    if bits % 32:
        raise ValueError(f"{bits} bits for flake is not divisible by 32")

    nbytes_rnd = (bits // 8) - 6

    ts = time.time() if ts is None else ts
    milliseconds = int(ts * 1000)
    timedata = milliseconds.to_bytes(6, "big", signed=False)
    counter = _COUNTER[timedata]
    if counter == 0:
        # Init counter with random value
        counterdata = os.urandom(nbytes_rnd)
        startcount = int.from_bytes(counterdata, "big", signed=False)
        _COUNTER[timedata] = startcount
        counter = startcount
    counterdata = counter.to_bytes(nbytes_rnd, "big", signed=False)
    _COUNTER.update([timedata])
    flake_digest = timedata + counterdata
    return flake_digest


def flake_to_iso8601(flake_code):
    # type: (str) -> str
    """
    Extracts timestamp from flake and returns an ISO 8601 formated date.

    !!! Example
        ```python
        >>> import iscc_code as ic
        >>> ic.flake_to_iso8601("ISCC:OAAQC7XVGJIIJU4C")
        '2022-02-13T22:27:02.404'
        ```
    """
    flake_code = ic.iscc_normalize(flake_code)
    ic.iscc_validate(flake_code, strict=True)
    flake = ic.iscc_clean(flake_code)
    raw = ic.decode_base32(flake)
    ts = int.from_bytes(raw[2:8], "big", signed=False) / 1000
    return datetime.utcfromtimestamp(ts).isoformat(timespec='milliseconds')
