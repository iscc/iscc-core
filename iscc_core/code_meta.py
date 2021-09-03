# -*- coding: utf-8 -*-
from more_itertools import interleave, sliced, chunked
from iscc_core.base import META_NGRAM_SIZE
from iscc_core.utils import sliding_window
from iscc_core.simhash import similarity_hash
from blake3 import blake3


def meta_hash(title, extra="", ngram_size=META_NGRAM_SIZE):
    # type: (str, str) -> bytes
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

        # Interleave first half pf title and extra simhashes in 32-bit chunks
        chunks_simhash_digest = sliced(simhash_digest[:16], 4)
        chunks_extra_simhash_digest = sliced(extra_simhash_digest[:16], 4)
        interleaved = interleave(chunks_simhash_digest, chunks_extra_simhash_digest)
        simhash_digest = bytearray()
        for chunk in interleaved:
            simhash_digest += chunk

        simhash_digest = bytes(simhash_digest)

    return simhash_digest

