# -*- coding: utf-8 -*-
import xxhash
from iscc_core.minhash import minhash_256
from iscc_core.base import TEXT_NGRAM_SIZE
from iscc_core.utils import sliding_window


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
