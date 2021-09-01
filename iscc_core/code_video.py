# -*- coding: utf-8 -*-
from typing import Sequence, Tuple
from iscc_core.wtahash import wtahash


def hash_video(frame_signatures: Sequence[Tuple[int]]) -> bytes:
    """Compute video hash (latest algorithm)."""
    return hash_video_v0(frame_signatures)


def hash_video_v0(frame_signatures: Sequence[Tuple[int]]) -> bytes:
    """Compute video hash v0 from MP7 frame signatures."""
    sigs = set(frame_signatures)
    vecsum = [sum(col) for col in zip(*sigs)]
    video_hash_digest = wtahash(vecsum)
    return video_hash_digest
