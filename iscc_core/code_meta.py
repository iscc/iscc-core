# -*- coding: utf-8 -*-
"""
ISCC Meta-Code
"""
from more_itertools import interleave, sliced

from iscc_core import codec
from iscc_core.base import META_NGRAM_SIZE
from iscc_core.utils import sliding_window
from iscc_core.simhash import similarity_hash
from blake3 import blake3


def code_meta(title, extra="", bits=64):
    # type: (str, str, int) -> str
    """Create an ISCC Meta-Code with the latest standard algorithm.

    :param str title: Title of the work manifested in the digital asset.
    :param str extra: Optional additional text for disambiguation of the work.
    :returns str: ISCC Meta-Code
    """
    return code_meta_v0(title, extra, bits)


def code_meta_v0(title, extra="", bits=64):
    # type: (str, str, int) -> str
    """Create an ISCC Meta-Code with the algorithm v0."""
    digest = hash_meta_v0(title, extra)
    meta_code = codec.encode_component(
        mtype=codec.MT.META,
        stype=codec.ST.NONE,
        version=codec.VS.V0,
        length=bits,
        digest=digest,
    )
    return meta_code


def hash_meta_v0(title, extra="", ngram_size=META_NGRAM_SIZE):
    # type: (str, str, int) -> bytes
    """
    Calculate simmilarity preserving 256-bit hash digest from metadata.
    Text input should be stripped of markup, normalized and trimmed before hashing.
    If the extra field is supplied we create separate hashes for title and extra and
    interleave them in 32-bit chunks.
    """
    title = title.lower()
    title_n_grams = sliding_window(title, width=ngram_size)
    title_hash_digests = [blake3(s.encode("utf-8")).digest() for s in title_n_grams]
    simhash_digest = similarity_hash(title_hash_digests)

    # Simhash extra metadata
    if extra:
        extra = extra.lower()
        extra_n_grams = sliding_window(extra, width=ngram_size)
        extra_hash_digests = [blake3(s.encode("utf-8")).digest() for s in extra_n_grams]
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
