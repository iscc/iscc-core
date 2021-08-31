# -*- coding: utf-8 -*-
from typing import Iterable
from more_itertools import windowed, chunked, divide
from iscc_core.simhash import similarity_hash


def hash_audio(cv: Iterable[int]) -> bytes:
    return hash_audio_v0(cv)


def hash_audio_v0(cv: Iterable[int]) -> bytes:
    """Create 256-bit audio similarity hash from a chromaprint vector."""

    # Convert chrompaprint vector into list of 4 byte digests
    digests = [int_feature.to_bytes(4, "big", signed=True) for int_feature in cv]

    # Return identity hash if we have 0 digests
    if not digests:
        return b"\x00" * 32

    # Calculate simhash of digests as first 32-bit chunk of the hash
    parts = [similarity_hash(digests)]

    # Calculate separate 32-bit simhashes for each quarter of features (original order)
    for bucket in divide(4, digests):
        features = list(bucket)
        if features:
            parts.append(similarity_hash(features))
        else:
            parts.append(b"\x00\x00\x00\x00")

    # Calculate separate simhashes for each third of features (ordered by int value)
    cvs = sorted(cv)
    digests = [int_feature.to_bytes(4, "big", signed=True) for int_feature in cvs]
    for bucket in divide(3, digests):
        features = list(bucket)
        if features:
            parts.append(similarity_hash(features))
        else:
            parts.append(b"\x00\x00\x00\x00")
    return b"".join(parts)
