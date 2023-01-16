# -*- coding: utf-8 -*-
"""*A similarity preserving hash for plain-text content (soft hash).*

The ISCC Text-Code is generated from plain-text that has been extracted
from a media assets.

!!! Warning

    Plain-text extraction from documents in various formats (especially PDF) may
    yield very diffent results depending on the extraction tools being used.
    The [iscc-sdk](https://github.com/iscc/iscc-sdk) uses [Apache Tika](https://tika.apache.org)
    to extract text from documents for Text-Code generation.

**Algorithm overview**

- Apply [`text_collapse`][iscc_core.code_content_text.text_collapse] function to text input
- Count characters of collapsed text
- Apply [`soft_hash_text_v0`][iscc_core.code_content_text.soft_hash_text_v0] to collapsed text
"""
import unicodedata
import xxhash
import iscc_core as ic


__all__ = [
    "gen_text_code",
    "gen_text_code_v0",
    "soft_hash_text_v0",
    "text_collapse",
]


def gen_text_code(text, bits=ic.core_opts.text_bits):
    # type: (str, int) -> dict
    """
    Create an ISCC Text-Code with the latest standard algorithm.

    :param str text: Plain text for Text-Code creation.
    :param int bits: Bit-length (multiple of 32) for ISCC Code Hash (default 64).
    :return: ISCC schema instance with Text-Code and an aditional property `characters`
    :rtype: dict
    """
    return gen_text_code_v0(text, bits)


def gen_text_code_v0(text, bits=ic.core_opts.text_bits):
    # type: (str, int) -> dict
    """
    Create an ISCC Text-Code with algorithm v0.

    !!! note
        Any markup (like HTML tags or markdown) should be removed from the plain-text
        before passing it to this function.

    :param str text: Text for Text-Code creation
    :param int bits: Bit-length of ISCC Code Hash (default 64)
    :return: ISCC schema instance with Text-Code and an aditional property `characters`
    :rtype: dict
    """

    text = text_collapse(text)
    characters = len(text)
    digest = soft_hash_text_v0(text)

    text_code = ic.encode_component(
        mtype=ic.MT.CONTENT,
        stype=ic.ST_CC.TEXT,
        version=ic.VS.V0,
        bit_length=bits,
        digest=digest,
    )

    iscc = "ISCC:" + text_code

    return dict(iscc=iscc, characters=characters)


def soft_hash_text_v0(text):
    # type: (str) -> bytes
    """
    Creates a 256-bit similarity preserving hash for text input with algorithm v0.

    - Slide over text with a
      [`text_ngram_size`][iscc_core.options.CoreOptions.text_ngram_size] wide window
      and create [`xxh32`](https://cyan4973.github.io/xxHash/) hashes
    - Create a [`minhash_256`][iscc_core.minhash.alg_minhash_256] from the hashes generated
      in the previous step.

    !!! note

        Before passing text to this function it must be:

        - stripped of markup
        - normalized
        - stripped of whitespace
        - lowercased

    :param str text: Plain text to be hashed.
    :return: 256-bit similarity preserving byte hash.
    :rtype: bytes
    """
    ngrams = ic.sliding_window(text, ic.core_opts.text_ngram_size)
    features = [xxhash.xxh32_intdigest(s.encode("utf-8")) for s in ngrams]
    hash_digest = ic.alg_minhash_256(features)
    return hash_digest


def text_collapse(text):
    # type: (str) -> str
    """
    Normalize and simplify text for similarity hashing.

    - Decompose with NFD normalization.
    - Remove all whitespace characters and convert text to lower case
    - Filter control characters, marks (diacritics), and punctuation
    - Recombine with NFKC normalization.

    !!! note

        See: [Unicode normalization](https://unicode.org/reports/tr15/).

    :param str text: Plain text to be collapsed.
    :return: Collapsed plain text.
    :rtype: str
    """

    # Decompose with NFD
    text = unicodedata.normalize("NFD", text)

    # Remove all whitespace and convert text to lower case
    text = "".join(text.split()).lower()

    # Filter control characters, marks (diacritics), and punctuation
    text = "".join(
        ch for ch in text if unicodedata.category(ch)[0] not in ic.core_opts.text_unicode_filter
    )

    # Recombine
    text = unicodedata.normalize("NFKC", text)

    return text
