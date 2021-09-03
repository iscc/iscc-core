# -*- coding: utf-8 -*-
"""
ISCC Content-Code Audio

The Content-Code Audio is generated from a Chromaprint fingerprint provided as a vector
of 32-bit signed integers. (See https://acoustid.org/chromaprint).
Chromaprints are extracted with fpcalc 1.5.0 (see https://acoustid.org/chromaprint)
using the following command line parameters:

$ fpcalc -raw -json -signed -length 0 myaudiofile.mp3
"""
from typing import Iterable
from more_itertools import divide
from iscc_core.simhash import similarity_hash
from iscc_core import codec


def code_audio(cv: Iterable[int], bits=64) -> str:
    """Create an ISCC Content-Code Audio with the latest standard algorithm."""
    return code_audio_v0(cv, bits)


def code_audio_v0(cv: Iterable[int], bits=64) -> str:
    """Create an ISCC Content-Code Audio with algorithm v0."""
    digest = hash_audio_v0(cv)
    audio_code = codec.encode_component(
        codec.MT.CONTENT, codec.ST_CC.AUDIO, 0, bits, digest
    )
    return audio_code


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
