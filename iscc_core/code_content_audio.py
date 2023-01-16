# -*- coding: utf-8 -*-
"""*A similarity preserving hash for audio content (soft hash).*

Creates an ISCC object that provides an `iscc`-field with an Audio-Code and a
`duration`-field.

The Content-Code Audio is generated from a Chromaprint fingerprint provided as a vector of 32-bit
signed integers. The [iscc-sdk](https://github.com/iscc/iscc-sdk) uses
[fpcalc](https://acoustid.org/chromaprint) to extract Chromaprint vectors with the following
command line parameters:

`$ fpcalc -raw -json -signed -length 0 myaudiofile.mp3`
"""
from typing import Iterable
from more_itertools import divide
import iscc_core as ic


__all__ = [
    "gen_audio_code",
    "gen_audio_code_v0",
    "soft_hash_audio_v0",
]


def gen_audio_code(cv, bits=ic.core_opts.audio_bits):
    # type: (Iterable[int], int) -> dict
    """
    Create an ISCC Content-Code Audio with the latest standard algorithm.

    :param Iterable[int] cv: Chromaprint vector
    :param int bits: Bit-length resulting Content-Code Audio (multiple of 64)
    :return: ISCC object with Content-Code Audio
    :rtype: dict
    """
    return gen_audio_code_v0(cv, bits)


def gen_audio_code_v0(cv, bits=ic.core_opts.audio_bits):
    # type: (Iterable[int], int) -> dict
    """
    Create an ISCC Content-Code Audio with algorithm v0.

    :param Iterable[int] cv: Chromaprint vector
    :param int bits: Bit-length resulting Content-Code Audio (multiple of 64)
    :return: ISCC object with Content-Code Audio
    :rtype: dict
    """
    digest = soft_hash_audio_v0(cv, bits=bits)
    audio_code = ic.encode_component(
        mtype=ic.MT.CONTENT,
        stype=ic.ST_CC.AUDIO,
        version=ic.VS.V0,
        bit_length=bits,
        digest=digest,
    )
    iscc = "ISCC:" + audio_code
    return {"iscc": iscc}


def soft_hash_audio_v0(cv, bits=ic.core_opts.audio_bits):
    # type: (Iterable[int], int) -> bytes
    """
    Create audio similarity hash from a chromaprint vector.

    :param Iterable[int] cv: Chromaprint vector
    :param int bits: Bit-length resulting similarity hash (multiple of 32)
    :return: Audio-Hash digest
    :rtype: bytes
    """

    # Convert chrompaprint vector into list of 4 byte digests
    digests = [int_feature.to_bytes(4, "big", signed=True) for int_feature in cv]

    # Return identity hash if we have 0 digests
    if not digests:
        return b"\x00" * 32

    # Calculate simhash of digests as first 32-bit chunk of the hash
    parts = [ic.alg_simhash(digests)]

    bit_length = 32

    # Calculate separate 32-bit simhashes for each quarter of features (original order)
    for bucket in divide(4, digests):
        features = list(bucket)
        if features:
            parts.append(ic.alg_simhash(features))
        else:
            parts.append(b"\x00\x00\x00\x00")
        bit_length += 32
        if bit_length == bits:
            return b"".join(parts)

    # Calculate separate simhashes for each third of features (ordered by int value)
    cvs = sorted(cv)
    digests = [int_feature.to_bytes(4, "big", signed=True) for int_feature in cvs]
    for bucket in divide(3, digests):
        features = list(bucket)
        if features:
            parts.append(ic.alg_simhash(features))
        else:
            parts.append(b"\x00\x00\x00\x00")
        bit_length += 32
        if bit_length == bits:
            return b"".join(parts)

    return b"".join(parts)
