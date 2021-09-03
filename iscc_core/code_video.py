# -*- coding: utf-8 -*-
"""
ISCC Content-Code Video

The Content-Code Video is generated from MPEG-7 Video Frame Signatures.
Frame Signatures can be extracted with ffmpeg (see: https://www.ffmpeg.org/).


"""
from typing import Sequence, Tuple
from iscc_core.wtahash import wtahash
from iscc_core import codec


def code_video(frame_signatures: Sequence[Tuple[int]], bits=64) -> str:
    """Create an ISCC Content-Code Video with the latest standard algorithm."""
    return code_video_v0(frame_signatures, bits)


def code_video_v0(frame_signatures: Sequence[Tuple[int]], bits=64) -> str:
    """Create an ISCC Content-Code Video with algorithm v0."""
    nbytes = bits // 8
    header = codec.write_header(
        codec.MT.CONTENT, codec.ST_CC.VIDEO, version=0, length=bits
    )
    digest = hash_audio_v0(cv)[:nbytes]
    audio_code = codec.encode_base32(header + digest)
    return audio_code


def hash_video(frame_signatures: Sequence[Tuple[int]]) -> bytes:
    """Compute video hash (latest algorithm)."""
    return hash_video_v0(frame_signatures)


def hash_video_v0(frame_signatures: Sequence[Tuple[int]]) -> bytes:
    """Compute video hash v0 from MP7 frame signatures."""
    sigs = set(frame_signatures)
    vecsum = [sum(col) for col in zip(*sigs)]
    video_hash_digest = wtahash(vecsum)
    return video_hash_digest
