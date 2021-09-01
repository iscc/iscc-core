# -*- coding: utf-8 -*-
from iscc_core import code_video


def test_hash_video_0_features():
    assert code_video.hash_video([tuple([0] * 380)]) == b"\x00" * 32


def test_hash_video_range():
    frame_vectors = [tuple(range(380))]
    assert (
        code_video.hash_video(frame_vectors).hex()
        == "528f91431f7c4ad26932fc073a28cac93f21a3071a152fc2925bdaed1d190061"
    )


def test_hash_video_multiple_framevectors():
    fa = tuple([0, 1, 0, 2, 1] * 76)
    fb = tuple([1, 2, 1, 0, 2] * 76)
    frame_vectors = [fa, fb]
    assert (
        code_video.hash_video(frame_vectors).hex()
        == "9230d219501e00f42664b4bd206b000c98488635b0b03c010010ee00aaf93e43"
    )
