# -*- coding: utf-8 -*-
from typing import Generator, Sequence
import xxhash
from iscc_core.minhash import minhash_256
from iscc_core.base import TEXT_NGRAM_SIZE


def hash_text(text: str) -> bytes:
    """
    Create a 256-bit similarity preserving hash for text input with latest algorithm.
    """
    return hash_text_v0(text)


def hash_text_v0(text: str) -> bytes:
    """
    Create a 256-bit similarity preserving hash for text input with v0 algorithm.
    Text should be normalized before hash creation.
    """
    text = text.lower()
    ngrams = sliding_window(text, TEXT_NGRAM_SIZE)
    features = [xxhash.xxh32_intdigest(s.encode("utf-8")) for s in ngrams]
    hash_digest = minhash_256(features)
    return hash_digest


def sliding_window(seq, width):
    # type: (Sequence, int) -> Generator
    """
    Generate a sequence of equal "width" slices each advancing by one elemnt.
    All types that have a length and can be sliced are supported (list, tuple, str ...).
    The result type matches the type of the input sequence.
    Fragment slices smaller than the width at the end of the sequence are not produced.
    If "witdh" is smaller than the input sequence than one element will be returned that
    is shorter than the requested width.
    """
    assert width >= 2, "Sliding window width must be 2 or bigger."
    idx = range(max(len(seq) - width + 1, 1))
    return (seq[i : i + width] for i in idx)
