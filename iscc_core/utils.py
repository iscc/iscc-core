# -*- coding: utf-8 -*-
from typing import Generator, Sequence


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
