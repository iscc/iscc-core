# -*- coding: utf-8 -*-
"""
*A similarity preserving hash for audio content (soft hash).*

Creates a [ContentCodeAudio][iscc_core.ContentCodeAudio] object that provides a
`code`-field and a `duration`-field.

The Content-Code Audio is generated from a [Chromaprint](https://acoustid.org/chromaprint)
fingerprint provided as a vector of 32-bit signed integers.
Chromaprints are extracted with [fpcalc 1.5.0](https://acoustid.org/chromaprint)
using the following command line parameters:

`$ fpcalc -raw -json -signed -length 0 myaudiofile.mp3`
"""
from typing import Iterable
from more_itertools import divide

from iscc_core.schema import ContentCodeAudio
from iscc_core.simhash import similarity_hash
from iscc_core import codec
from iscc_core.options import opts


def gen_audio_code(cv, bits=opts.audio_bits):
    # type: (Iterable[int], int) -> ContentCodeAudio
    """Create an ISCC Content-Code Audio with the latest standard algorithm.

    :param Iterable[int] cv: Chromaprint vector
    :param int bits: Bit-length resulting Content-Code Audio (multiple of 64)
    :return: ContentCodeAudio object
    :rtype: ContentCodeAudio
    """
    return gen_audio_code_v0(cv, bits)


def gen_audio_code_v0(cv, bits=opts.audio_bits):
    # type: (Iterable[int], int) -> ContentCodeAudio
    """Create an ISCC Content-Code Audio with algorithm v0.

    :param Iterable[int] cv: Chromaprint vector
    :param int bits: Bit-length resulting Content-Code Audio (multiple of 64)
    :return: ContentCodeAudio object
    :rtype: ContentCodeAudio
    """
    digest = soft_hash_audio_v0(cv)
    audio_code = codec.encode_component(
        mtype=codec.MT.CONTENT,
        stype=codec.ST_CC.AUDIO,
        version=codec.VS.V0,
        length=bits,
        digest=digest,
    )
    return ContentCodeAudio(iscc=audio_code)


def soft_hash_audio_v0(cv):
    # type: (Iterable[int]) -> bytes
    """Create 256-bit audio similarity hash from a chromaprint vector.

    :param Iterable[int] cv: Chromaprint vector
    :return: 256-bit Audio-Hash digest
    :rtype: bytes
    """

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
