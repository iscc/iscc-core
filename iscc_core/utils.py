# -*- coding: utf-8 -*-
from typing import Generator, Sequence, Tuple
from bitarray import bitarray
from bitarray.util import count_xor
import iscc_core as ic


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
    assert width >= 2, "Sliding window width must be 2 or bigger."
    idx = range(max(len(seq) - width + 1, 1))
    return (seq[i : i + width] for i in idx)


def similarity(a, b):
    # type: (str, str) -> int
    """
    Calculate similarity of ISCC codes as a percentage value (0-100).

    MainType, SubType, Version and Length of the codes must be the same.

    :param a: ISCC a
    :param b: ISCC b
    :return: Similarity of ISCC a and b in percent (based on hamming distance)
    :rtype: int
    """
    a, b = _safe_unpack(a, b)
    hdist = hamming_distance(a, b)
    nbits = len(a) * 8
    sim = int(((nbits - hdist) / nbits) * 100)
    return sim


def distance(a, b):
    # type: (str, str) -> int
    """
    Calculate hamming distance of ISCC codes.

    MainType, SubType, Version and Length of the codes must be the same.

    :param a: ISCC a
    :param b: ISCC b
    :return: Hamming distanced in number of bits.
    :rtype: int
    """
    a, b = _safe_unpack(a, b)
    return hamming_distance(a, b)


def hamming_distance(a, b):
    # type: (bytes, bytes) -> int
    """
    Calculate hamming distance for binary hash digests of equal length.

    :param bytes a: binary hash digest
    :param bytes b: binary hash digest
    :return: Hamming distance in number of bits.
    :rtype: int
    """
    assert len(a) == len(b), f"Hash diggest of unequal length: {len(a)} vs {len(b)}"
    ba, bb = bitarray(), bitarray()
    ba.frombytes(a)
    bb.frombytes(b)
    return count_xor(ba, bb)


def _safe_unpack(a, b):
    # type: (str, str) -> Tuple[bytes, bytes]
    """
    Unpack two ISCC codes and return their hash digests if their headers match.

    :param a: ISCC a
    :param b: ISCC b
    :return: Tuple with hash digests of a and b
    :rtype: Tuple[bytes, bytes]
    :raise ValueError: If ISCC headers don´t match
    """
    a, b = ic.clean(ic.normalize(a)), ic.clean(ic.normalize(b))
    a, b = ic.decode_base32(a), ic.decode_base32(b)
    a, b = ic.read_header(a), ic.read_header(b)
    if not a[:-1] == b[:-1]:
        raise ValueError(f"ISCC headers don´t match: {a}, {b}")
    return a[-1], b[-1]
