# -*- coding: utf-8 -*-
"""
ISCC Content-Code Text - A similarity preserving hash for text content (soft hash).

The Content-Code Text is generated from plain-text that has been extracted from
different media formats. The plain-text input has to be normalized before using this
algorithm.
"""
import xxhash
from iscc_core.minhash import minhash_256
from iscc_core.base import TEXT_NGRAM_SIZE
from iscc_core.utils import sliding_window
from iscc_core import codec


def code_text(text, bits=64):
    # type: (str, int) -> str
    """Create an ISCC Content-Code Text with the latest standard algorithm.

    :param str text: Normalized text for Text-Code creation.
    :param int bits: Bit-length of ISCC Code Hash (default 64).
    :returns str: ISCC Content-Code Text.
    """
    return code_text_v0(text, bits)


def code_text_v0(text, bits=64):
    # type: (str, int) -> str
    """Create ISCC Content-Code Text with algorithm v0"""
    digest = hash_text_v0(text)
    text_code = codec.encode_component(
        mtype=codec.MT.CONTENT,
        stype=codec.ST_CC.TEXT,
        version=codec.VS.V0,
        length=bits,
        digest=digest,
    )
    return text_code


def hash_text_v0(text):
    # type: (str) -> bytes
    """
    Create a 256-bit similarity preserving hash for text input with v0 algorithm.
    Text should be normalized before hash creation.
    """
    text = text.lower()
    ngrams = sliding_window(text, TEXT_NGRAM_SIZE)
    features = [xxhash.xxh32_intdigest(s.encode("utf-8")) for s in ngrams]
    hash_digest = minhash_256(features)
    return hash_digest
