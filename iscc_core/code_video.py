# -*- coding: utf-8 -*-
"""
ISCC Content-Code Video

The Content-Code Video is generated from MPEG-7 Video Frame Signatures.
Frame Signatures can be extracted with ffmpeg (see: https://www.ffmpeg.org/).
"""
from typing import Sequence, Tuple
from iscc_core.wtahash import wtahash
from iscc_core import codec


def code_video(frame_signatures, bits=64):
    # type: (Sequence[Tuple[int]], int) -> str
    """Create an ISCC Content-Code Video with the latest standard algorithm."""
    return code_video_v0(frame_signatures, bits)


def code_video_v0(frame_signatures, bits=64):
    # type: (Sequence[Tuple[int]], int) -> str
    """Create an ISCC Content-Code Video with algorithm v0."""
    digest = hash_video_v0(frame_signatures)
    video_code = codec.encode_component(
        codec.MT.CONTENT, codec.ST_CC.VIDEO, version=0, length=bits, digest=digest
    )
    return video_code


def hash_video_v0(frame_signatures):
    # type: (Sequence[Tuple[int]]) -> bytes
    """Compute 256-bit video hash v0 from MP7 frame signatures."""
    sigs = set(frame_signatures)
    vecsum = [sum(col) for col in zip(*sigs)]
    video_hash_digest = wtahash(vecsum)
    return video_hash_digest
