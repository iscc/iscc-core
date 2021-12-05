# -*- coding: utf-8 -*-
"""
The Meta-Code is the first component of a canonical ISCC. It is calculated as a
similarity preserving hash from the metadata of a digital asset. The purpose of the
Meta-Code is the discovery of digital assets with similar metadata or spelling mistakes.

The metadata supplied to the algorithm is called *seed metadata*.

*Seed metadata* is composed of a `title` and an optional generic `extra`-field that
contains descriptive, industry-sector or use-case specific metadata in textual or
binary form (e.g. file headers). We do not prescribe a particular schema.
"""
from more_itertools import interleave, sliced
from iscc_core.code_content_text import normalize_text
from iscc_core.codec import MT, ST, VS, encode_base64, encode_component
from iscc_core.schema import MetaCode
from iscc_core.utils import sliding_window
from iscc_core.simhash import similarity_hash
from iscc_core.options import opts
from blake3 import blake3
from typing import Union


def gen_meta_code(title, extra=None, bits=opts.meta_bits):
    # type: (str, Union[str,bytes,None], int) -> MetaCode
    """Create an ISCC Meta-Code using the latest standard algorithm.

    Applications that generate ISCCs should prioritize explicitly passed `title`
    information. If not available they should try to extract a title form the digital
    asset itself. If extraction fails, the application should resort to a normalized
    filename before falling back to an empty string.

    Optional additional metadata may be supplied via the `extra`-field.
    The input can be:

    - A textual description of the identified work for disambiguation purposes
    - Structured (JSON) metadata conforming to an industry specific metadata schema
    - Raw bitstream file headers automatically extracted binary file headers
    - A pre-existing industry-specific identifier string

    !!! note
        It is recommended to use the minimal metadata required to disambiguate the work
        manifested by the digital asset.

    :param str title: Title of the work manifested by the digital asset
    :param Union[str,bytes,None] extra: Optional metadata for disambiguation
    :param int bits: Bit-length of resulting Meta-Code (multiple of 64)
    :return: ISCC Meta-Code
    :rtype: MetaCode
    """
    return gen_meta_code_v0(title, extra=extra, bits=bits)


def gen_meta_code_v0(title, extra=None, bits=opts.meta_bits):
    # type: (str, Union[str,bytes,None], int) -> MetaCode
    """Create an ISCC Meta-Code with the algorithm version 0.

    :param str title: Title of the work manifested by the digital asset
    :param Union[str,bytes,None] extra: Optional metadata for disambiguation
    :param int bits: Bit-length of resulting Meta-Code (multiple of 64)
    :return: ISCC Meta-Code
    :rtype: MetaCode
    """

    # 1. Normalize title
    title = "" if title is None else title
    title = normalize_text(title)
    title = trim_text(title, opts.meta_trim_title)

    # 2. Normalize extra
    if extra in (None, ""):
        extra = None
        metahash_payload = title.encode("utf-8")
    elif isinstance(extra, str):
        metahash_payload = extra.encode("utf-8")  # assumed JCS normalized if JSON
        extra = normalize_text(extra)
        extra = trim_text(extra, opts.meta_trim_extra)
    elif isinstance(extra, bytes):
        metahash_payload = extra
        extra = extra[: opts.meta_trim_extra]
    else:
        raise ValueError("parameter `extra` must be of type str or bytes!")

    digest = soft_hash_meta_v0(title, extra)
    meta_code = encode_component(
        mtype=MT.META,
        stype=ST.NONE,
        version=VS.V0,
        length=bits,
        digest=digest,
    )

    metahash = blake3(metahash_payload).hexdigest()

    if isinstance(extra, bytes):
        extra = encode_base64(extra)
        binary = True
    else:
        binary = False

    if not title:
        title = None
    mc_obj = MetaCode(
        iscc=meta_code, title=title, extra=extra, binary=binary, metahash=metahash
    )
    return mc_obj


def soft_hash_meta_v0(title, extra=None):
    # type: (str, Union[str,bytes,None]) -> bytes
    """Calculate simmilarity preserving 256-bit hash digest from asset metadata.

    Textual input should be stripped of markup, normalized and trimmed before hashing.
    Json metadata should be normalized with
    [JCS](https://tools.ietf.org/id/draft-rundgren-json-canonicalization-scheme-00.html)

    !!! note
        The processing algorithm depends on the type of the `extra` input.
        If the `extra` field is supplied and non-empty, we create separate hashes for
        `title` and `extra` and interleave them in 32-bit chunks:

        - If the input is `None` or an empty `str`/`bytes` object the Meta-Hash will
        be generated from the `title`-field only.

        - If the `extra`-input is a non-empty **text** string (str) the string is
        lower-cased and the processing unit is an utf-8 endoded character
        (possibly multibyte). The resulting hash is interleaved with the `title`-hash.

        - If the `extra`-input is a non-empty **bytes** object the processing is done
        bytewise and the resulting hash is interleaved with the `title`-hash.

    :param str title: Title of the work manifested in the digital asset
    :param Union[str,bytes,None] extra: Additional metadata for disambiguation
    :return: 256-bit simhash digest for Meta-Code
    :rtype: bytes
    """
    title = title.lower()
    title_n_grams = sliding_window(title, width=opts.meta_ngram_size_title)
    title_hash_digests = [blake3(s.encode("utf-8")).digest() for s in title_n_grams]
    simhash_digest = similarity_hash(title_hash_digests)

    if extra in (None, "", b""):
        return simhash_digest
    else:
        # Augment with interleaved hash for extra metadata
        if isinstance(extra, bytes):
            # Raw bytes are handled per byte
            extra_n_grams = sliding_window(
                extra, width=opts.meta_ngram_size_extra_binary
            )
            extra_hash_digests = [blake3(ngram).digest() for ngram in extra_n_grams]
        elif isinstance(extra, str):
            # Text is lower cased and handled per character (multibyte)
            extra = extra.lower()
            extra_n_grams = sliding_window(extra, width=opts.meta_ngram_size_extra_text)
            extra_hash_digests = [
                blake3(s.encode("utf-8")).digest() for s in extra_n_grams
            ]
        else:
            raise ValueError("parameter `extra` must be of type str or bytes!")

        extra_simhash_digest = similarity_hash(extra_hash_digests)

        # Interleave first half of title and extra simhashes in 32-bit chunks
        chunks_simhash_digest = sliced(simhash_digest[:16], 4)
        chunks_extra_simhash_digest = sliced(extra_simhash_digest[:16], 4)
        interleaved = interleave(chunks_simhash_digest, chunks_extra_simhash_digest)
        simhash_digest = bytearray()
        for chunk in interleaved:
            simhash_digest += chunk

        simhash_digest = bytes(simhash_digest)

        return simhash_digest


def trim_text(text, nbytes):
    # type: (str, int) -> str
    """Trim text such that its utf-8 encoded size does not exceed `nbytes`."""
    return text.encode("utf-8")[:nbytes].decode("utf-8", "ignore").strip()
