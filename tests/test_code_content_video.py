# -*- coding: utf-8 -*-
from iscc_core import code_content_video


def test_hash_video_v0_features():
    assert code_content_video.soft_hash_video_v0([tuple([0] * 380)]) == b"\x00" * 32


def test_hash_video_v0_range():
    frame_vectors = [tuple(range(380))]
    assert (
        code_content_video.soft_hash_video_v0(frame_vectors).hex()
        == "528f91431f7c4ad26932fc073a28cac93f21a3071a152fc2925bdaed1d190061"
    )


def test_hash_video_v0_multiple_framevectors():
    fa = tuple([0, 1, 0, 2, 1] * 76)
    fb = tuple([1, 2, 1, 0, 2] * 76)
    frame_vectors = [fa, fb]
    assert (
        code_content_video.soft_hash_video_v0(frame_vectors).hex()
        == "9230d219501e00f42664b4bd206b000c98488635b0b03c010010ee00aaf93e43"
    )


def test_code_video_v0_features():
    assert (
        code_content_video.gen_video_code_v0([tuple([0] * 380)]).code
        == "EMAQAAAAAAAAAAAA"
    )


def test_code_video_v0_range_128():
    frame_vectors = [tuple(range(380))]
    assert (
        code_content_video.gen_video_code_v0(frame_vectors, bits=128).code
        == "EMBVFD4RIMPXYSWSNEZPYBZ2FDFMS"
    )


def test_code_video_v0_multiple_framevectors_256():
    fa = tuple([0, 1, 0, 2, 1] * 76)
    fb = tuple([1, 2, 1, 0, 2] * 76)
    frame_vectors = [fa, fb]
    assert (
        code_content_video.gen_video_code_v0(frame_vectors, bits=256).code
        == "EMDZEMGSDFIB4AHUEZSLJPJANMAAZGCIQY23BMB4AEABB3QAVL4T4QY"
    )
