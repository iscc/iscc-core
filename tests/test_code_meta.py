# -*- coding: utf-8 -*-
from iscc_core import code_meta


def test_hash_meta_v0_empty():
    m = code_meta.hash_meta_v0("")
    assert len(m) == 32
    assert m.hex() == "af1349b9f5f9a1a6a0404dea36dcc9499bcb25c9adc112b7cc9a93cae41f3262"


def test_hash_meta_v0_extra_only():
    m = code_meta.hash_meta_v0("", "Hello")
    assert len(m) == 32
    assert m.hex() == "af1349b9652ce5bbf5f9a1a63fd7018aa0404dea8746265c36dcc949d8a542f4"


def test_hash_meta_v0_interleaved():
    ma = code_meta.hash_meta_v0("", "")
    mb = code_meta.hash_meta_v0("", "hello")
    assert ma[:4] == mb[:4]
    assert ma[4:8] == mb[8:12]


def test_code_meta_v0_empty_default():
    m = code_meta.gen_meta_code_v0("")
    assert m == "AAA26E2JXH27TING"


def test_code_meta_v0_extra_only_128_bits():
    m = code_meta.gen_meta_code_v0("", "Hello", 128)
    assert m == "AAB26E2JXFSSZZN36X42DJR724AYU"


def test_code_meta_v0_interleaved():
    ma = code_meta.gen_meta_code_v0("", "")
    mb = code_meta.gen_meta_code_v0("", "hello")
    assert ma == "AAA26E2JXH27TING"
    assert mb == "AAA26E2JXFSSZZN3"
