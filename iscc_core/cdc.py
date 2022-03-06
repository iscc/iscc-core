# -*- coding: utf-8 -*-
"""Compatible with [fastcdc](https://pypi.org/project/fastcdc/)"""
import io
from math import log2
from typing import Generator
import iscc_core as ic


__all__ = [
    "alg_cdc_chunks",
]


def alg_cdc_chunks(data, utf32, avg_chunk_size=ic.core_opts.data_avg_chunk_size):
    # type: (Data, bool, int) -> Generator[bytes, None, None]
    """
    A generator that yields data-dependent chunks for `data`.

    Usage Example:

    ```python
    for chunk in cdc_data_chunks(data):
        hash(chunk)
    ```

    :param bytes data: Raw data for variable sized chunking.
    :param bool utf32: If true assume we are chunking text that is utf32 encoded.
    :param int avg_chunk_size: Target chunk size in number of bytes.
    :return: A generator that yields data chunks of variable sizes.
    :rtype: Generator[bytes]
    """

    stream = io.BytesIO(data)
    buffer = stream.read(ic.core_opts.io_read_size)
    if not buffer:
        yield b""

    mi, ma, cs, mask_s, mask_l = alg_cdc_params(avg_chunk_size)

    buffer = memoryview(buffer)
    while buffer:
        if len(buffer) <= ma:
            buffer = memoryview(bytes(buffer) + stream.read(ic.core_opts.io_read_size))
        cut_point = alg_cdc_offset(buffer, mi, ma, cs, mask_s, mask_l)

        # Make sure cut points are at 4-byte aligned for utf32 encoded text
        if utf32:
            cut_point -= cut_point % 4

        yield bytes(buffer[:cut_point])
        buffer = buffer[cut_point:]


def alg_cdc_offset(buffer, mi, ma, cs, mask_s, mask_l):
    # type: (ic.Data, int, int, int, int, int) -> int
    """
    Find breakpoint offset for a given buffer.

    :param Data buffer: The data to be chunked.
    :param int mi: Minimum chunk size.
    :param int ma: Maximung chunk size.
    :param int cs: Center size.
    :param int mask_s: Small mask.
    :param int mask_l: Large mask.
    :return: Offset of dynamic cutpoint in number of bytes.
    :rtype: int
    """

    pattern = 0
    i = mi
    size = len(buffer)
    barrier = min(cs, size)
    while i < barrier:
        pattern = (pattern >> 1) + ic.core_opts.cdc_gear[buffer[i]]
        if not pattern & mask_s:
            return i + 1
        i += 1
    barrier = min(ma, size)
    while i < barrier:
        pattern = (pattern >> 1) + ic.core_opts.cdc_gear[buffer[i]]
        if not pattern & mask_l:
            return i + 1
        i += 1
    return i


def alg_cdc_params(avg_size: int) -> tuple:
    """
    Calculate CDC parameters

    :param int avg_size: Target average size of chunks in number of bytes.
    :returns: Tuple of (min_size, max_size, center_size, mask_s, mask_l).
    """
    ceil_div = lambda x, y: (x + y - 1) // y
    mask = lambda b: 2**b - 1
    min_size = avg_size // 4
    max_size = avg_size * 8
    offset = min_size + ceil_div(min_size, 2)
    center_size = avg_size - offset
    bits = round(log2(avg_size))
    mask_s = mask(bits + 1)
    mask_l = mask(bits - 1)
    return min_size, max_size, center_size, mask_s, mask_l
