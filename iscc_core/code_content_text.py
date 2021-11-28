# -*- coding: utf-8 -*-
"""
A similarity preserving hash for text content (soft hash).
The **ISCC Content-Code Text** is generated from plain-text that has been extracted
from different media assets.
"""
import unicodedata
from typing import Union
import xxhash
from iscc_core.minhash import minhash_256
from iscc_core.models import ContentCodeText
from iscc_core.options import opts
from iscc_core.utils import sliding_window
from iscc_core import codec


Text = Union[str, bytes]


def gen_text_code(text, bits=opts.text_bits):
    # type: (Text, int) -> ContentCodeText
    """Create an ISCC Content-Code-Text with the latest standard algorithm.

    !!! note
        If `text` input includes markup (like HTML tags) it must be removed beforehand.

    :param Text text: Plain text for Text-Code creation.
    :param int bits: Bit-length (multiple of 32) for ISCC Code Hash (default 64).
    :return: TextCode with properties: code, characters
    :rtype: ContentCodeText
    """
    return gen_text_code_v0(text, bits)


def gen_text_code_v0(text, bits=opts.text_bits):
    # type: (Text, int) -> ContentCodeText
    """Create ISCC Content-Code-Text with algorithm v0

    - Normalize and lowercase text.
    - Create a Simhash from the tokens generated by a 13-character sliding window.
    - Encode resulting byte hash with ISCC codec.

    :param Text text: Normalized text for Text-Code creation.
    :param int bits: Bit-length of ISCC Code Hash (default 64).
    :return: TextCode with properties: code, characters
    :rtype: ContentCodeText
    """
    text_norm = normalize_text(text)
    characters = len(text_norm)
    text_lower = text_norm.lower()
    digest = soft_hash_text_v0(text_lower)
    text_code = codec.encode_component(
        mtype=codec.MT.CONTENT,
        stype=codec.ST_CC.TEXT,
        version=codec.VS.V0,
        length=bits,
        digest=digest,
    )
    return ContentCodeText(code=text_code, characters=characters)


def normalize_text(text):
    # type: (Text) -> str
    """Unicode normalization and character filtering.

    - Decode to Unicode.
    - Remove leading/trailing whitespace.
    - Decompose with NFD normalization.
    - Filter special characters and whitespace.
    - Remove duplicate whitespace.
    - Recombine with NFKC normalization.

    :param Text text: Plain text to be normalized.
    :return: Normalized plain text.
    :rtype: str
    """

    # 1. Convert bytes to str
    if isinstance(text, bytes):
        text = text.decode("utf-8")

    # 2. Remove leading/trailing whitespace
    text_stripped = text.strip()

    # 3. Decompose with NFD
    text_decomposed = unicodedata.normalize("NFD", text_stripped)

    # 4. Filter
    chars = []
    for c in text_decomposed:
        cat = unicodedata.category(c)
        if cat not in opts.text_unicode_filter:
            chars.append(c)
        elif c in opts.text_whitespace:
            chars.append(c)
    text_filtered = "".join(chars)

    # 5. Collapse consecutive whitespace
    wsproc_text = " ".join(text_filtered.split())

    # 6. Recombine
    recombined = unicodedata.normalize("NFKC", wsproc_text)

    return recombined


def soft_hash_text_v0(text):
    # type: (str) -> bytes
    """
    Create a 256-bit similarity preserving hash for text input with v0 algorithm.
    Text should be stripped of markup, normalized and lowercased before hash creation.

    :param str text: Plain text to be hashed.
    :return: 256-bit similarity preserving byte hash.
    :rtype: bytes
    """
    ngrams = sliding_window(text, opts.text_ngram_size)
    features = [xxhash.xxh32_intdigest(s.encode("utf-8")) for s in ngrams]
    hash_digest = minhash_256(features)
    return hash_digest
