# -*- coding: utf-8 -*-
from iscc_core import code_content_audio


def test_hash_audio_001_empty():
    cv = []
    assert (
        code_content_audio.soft_hash_audio_v0(cv).hex()
        == "0000000000000000000000000000000000000000000000000000000000000000"
    )


def test_hash_audio_002_single():
    cv = [1]
    assert (
        code_content_audio.soft_hash_audio_v0(cv).hex()
        == "0000000100000001000000000000000000000000000000010000000000000000"
    )


def test_hash_audio_003_short():
    cv = [1, 2]
    assert (
        code_content_audio.soft_hash_audio_v0(cv).hex()
        == "0000000300000001000000020000000000000000000000010000000200000000"
    )


def test_hash_audio_004_signed():
    cv = [-1, 0, 1]
    assert (
        code_content_audio.soft_hash_audio_v0(cv).hex()
        == "00000001ffffffff000000000000000100000000ffffffff0000000000000001"
    )


def test_hash_audio_005_sample():
    assert (
        code_content_audio.soft_hash_audio_v0(CHROMA_VECTOR).hex()
        == "6a24a22672e4e2a33a4e88876a84a0266a24a2263a4ea0836264a22468842a2f"
    )


def test_code_audio_v0_default():
    assert (
        code_content_audio.gen_audio_code_v0(CHROMA_VECTOR).code == "EIAWUJFCEZZOJYVD"
    )


def test_code_audio_v0_32bits():
    assert (
        code_content_audio.gen_audio_code_v0(CHROMA_VECTOR, bits=32).code
        == "EIAGUJFCEY"
    )


def test_code_audio_v0_64bits():
    assert (
        code_content_audio.gen_audio_code_v0(CHROMA_VECTOR, bits=64).code
        == "EIAWUJFCEZZOJYVD"
    )


def test_code_audio_v0_128bits():
    assert (
        code_content_audio.gen_audio_code_v0(CHROMA_VECTOR, bits=128).code
        == "EIBWUJFCEZZOJYVDHJHIRB3KQSQCM"
    )


def test_code_audio_v0_256bits():
    assert (
        code_content_audio.gen_audio_code_v0(CHROMA_VECTOR, bits=256).code
        == "EIDWUJFCEZZOJYVDHJHIRB3KQSQCM2REUITDUTVAQNRGJIRENCCCULY"
    )


CHROMA_VECTOR = [
    684003877,
    683946551,
    1749295639,
    2017796679,
    2026256086,
    2022066918,
    2022001639,
    2021968035,
    2038741139,
    2059709571,
    503750851,
    369541315,
    320225426,
    289292450,
    830368930,
    838789539,
    1940835201,
    1928186752,
    1651297920,
    1651283600,
    1650959072,
    1655022116,
    1722069540,
    1726259749,
    1713694254,
    1847914286,
    1847912494,
    1780832302,
    -362410962,
    -352973810,
    1809196111,
    1770397775,
    1753686797,
    683942429,
    943989277,
    943989255,
    944121430,
    952503910,
    948374246,
    948717799,
    1485621411,
    462203011,
    508470403,
    370053251,
    303988867,
    322879651,
    322892963,
    862907811,
    1928256417,
    1928317841,
    1651297152,
    1647091344,
    1650827936,
    1659216416,
    1722069540,
    1726263844,
    1717887533,
    1713696302,
    1847912494,
    1847883822,
    -366540754,
    -345633778,
    -336184242,
    1771447375,
    1753620815,
    1757684255,
    675553815,
    943989255,
    944120390,
    952508006,
    948308582,
    948718050,
    411879650,
    428648578,
    516861059,
    370057347,
    303988865,
    306086033,
    306086051,
    841919649,
    846133665,
    1919929264,
    1647168400,
    1647101584,
    1650827936,
    1659216484,
    1671733796,
    1738838588,
    1717887517,
    1713696302,
    1847913774,
    1847912494,
    1780960302,
    -362410978,
    -336196594,
    1775641678,
    1770397775,
    1753555743,
    683942429,
    943989271,
    944185926,
    2026255094,
    2022051494,
    2021919654,
]
