# -*- coding: utf-8 -*-
"""*A similarity preserving hash for plain-text content (soft hash).*

The ISCC Text-Code is generated from plain-text that has been extracted
from a media assets.

!!! tip

    Plain-text extraction from documents in various formats (especially PDF) may
    yield very diffent results depending on the extraction tools being used.
    For **reproducible Text-Code generation** use
    [Apache Tika v2.2.1](https://tika.apache.org/2.2.1/index.html) to extract text
    from your documents.

**Algorithm overview**:

- Normalize text using [`normalize_text`][iscc_core.code_content_text.normalize_text]
  function
- Count characters of normalized text
- Remove all whitespace
- Lowercase text
- Apply function [`soft_hash_text_v0`][iscc_core.code_content_text.soft_hash_text_v0]
  to text
"""
import unicodedata
from typing import Union
import xxhash
from iscc_core.minhash import minhash_256
from iscc_core.schema import ISCC
from iscc_core.utils import sliding_window
from iscc_core import codec, core_opts


Text = Union[str, bytes]


def gen_text_code(text, bits=core_opts.text_bits):
    # type: (Text, int) -> ISCC
    """
    Create an ISCC Text-Code with the latest standard algorithm.

    :param Text text: Plain text for Text-Code creation.
    :param int bits: Bit-length (multiple of 32) for ISCC Code Hash (default 64).
    :return: ISCC schema instance with Text-Code and an aditional property `characters`
    :rtype: ISCC
    """
    return gen_text_code_v0(text, bits)


def gen_text_code_v0(text, bits=core_opts.text_bits):
    # type: (Text, int) -> ISCC
    """
    Create an ISCC Text-Code with algorithm v0.

    !!! note
        Any markup (like HTML tags or markdown) should be removed from the plain-text
        before passing it to this function.

    :param Text text: Text for Text-Code creation
    :param int bits: Bit-length of ISCC Code Hash (default 64)
    :return: ISCC schema instance with Text-Code and an aditional property `characters`
    :rtype: ISCC
    """

    text = normalize_text(text)
    characters = len(text)
    text = "".join(text.split())
    text = text.lower()
    digest = soft_hash_text_v0(text)

    text_code = codec.encode_component(
        mtype=codec.MT.CONTENT,
        stype=codec.ST_CC.TEXT,
        version=codec.VS.V0,
        bit_length=bits,
        digest=digest,
    )

    iscc = "ISCC:" + text_code

    return ISCC(iscc=iscc, characters=characters)


def normalize_text(text):
    # type: (Text) -> str
    """
    [Unicode normalization](https://unicode.org/reports/tr15/) and character filtering.

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
        if cat not in core_opts.text_unicode_filter:
            chars.append(c)
        elif c in core_opts.text_whitespace:
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
    Creates a 256-bit similarity preserving hash for text input with algorithm v0.

    - Slide over text with a
      [`text_ngram_size`][iscc_core.options.CoreOptions.text_ngram_size] wide window
      and create [`xxh32`](https://cyan4973.github.io/xxHash/) hashes
    - Create a [`minhash_256`][iscc_core.minhash.minhash_256] from the hashes generated
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
    ngrams = sliding_window(text, core_opts.text_ngram_size)
    features = [xxhash.xxh32_intdigest(s.encode("utf-8")) for s in ngrams]
    hash_digest = minhash_256(features)
    return hash_digest
