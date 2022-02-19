# -*- coding: utf-8 -*-
"""*A unique, time-sorted identifier composed of an 48-bit timestamp and 16 to 208 bit randomness.*

The ISCC Flake-Code is a unique identifier for distributed ID generation. The 64-bit version
can be used as efficient surrogate key in database systems. It has guaranteed uniqueness if
generated from a singele process and is time sortable in integer and base32hex representation.
The 128-bit version is a K-sortable, globally unique identifier for use in distributed systems and
is compatible with UUID.

!!! example

    ```python
    >>> import iscc_core as ic
    >>> ic.gen_flake_code(bits=64)
    {'iscc': 'ISCC:OAAQC7YN7PG2XOR4'}

    >>> ic.gen_flake_code(bits=128)
    {'iscc': 'ISCC:OABQC7YN7RJGUUTLKDSKBXO25MA5E'}

    # Or use the convenience Flake class for easy access to different representations

    >>> flake = ic.Flake(bits=64)
    >>> flake.iscc
    'ISCC:OAAQC7YOADBZYNF7'

    >>> flake.time
    '2022-02-18T18:03:25.468'

    >>> flake.int
    107820312524764351

    >>> flake.string
    '05VGS063JGQBU'
    ```
"""
import os
import time
from collections import Counter
from typing import Optional
import iscc_core as ic


__all__ = [
    "gen_flake_code",
    "gen_flake_code_v0",
    "uid_flake_v0",
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

    digest = uid_flake_v0(bits=bits)
    flake_code = ic.encode_component(
        mtype=ic.MT.FLAKE, stype=ic.ST.NONE, version=ic.VS.V0, bit_length=bits, digest=digest
    )
    iscc = "ISCC:" + flake_code
    return {"iscc": iscc}


def uid_flake_v0(ts=None, bits=ic.core_opts.flake_bits):
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
