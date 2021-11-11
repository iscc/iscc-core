# -*- coding: utf-8 -*-
from iscc_core import code_meta


def test_gen_meta_code_title_none():
    m = code_meta.gen_meta_code(None)
    assert m == "AAA26E2JXH27TING"


def test_gen_meta_code_title_empty_str():
    m = code_meta.gen_meta_code("")
    assert m == "AAA26E2JXH27TING"


def test_gen_meta_code_title_with_extra():
    empty = "AAA26E2JXH27TING"
    m = code_meta.gen_meta_code(None, None)
    assert m == empty
    m = code_meta.gen_meta_code(None, "")
    assert m == empty
    m = code_meta.gen_meta_code("", None)
    assert m == empty
    m = code_meta.gen_meta_code("", "")
    assert m == empty


def test_gen_meta_code_text_vs_bytes():
    m = code_meta.gen_meta_code("", "hello world")
    assert m == "AAA26E2JXH733ZNM"
    m = code_meta.gen_meta_code("", b"hello world")
    assert m == "AEA26E2JXH733ZNM"
    m = code_meta.gen_meta_code("", b"\x80")  # not utf-8 decodable
    assert m == "AEA26E2JXG56NKPV"


def test_gen_meta_code_title_only():
    m = code_meta.gen_meta_code("Hello World")
    assert m == "AAA77PPFVS6JDUQB"


def test_hash_meta_v0_empty_title_str():
    m = code_meta.hash_meta_v0("")
    assert len(m) == 32
    assert m.hex() == "af1349b9f5f9a1a6a0404dea36dcc9499bcb25c9adc112b7cc9a93cae41f3262"


def test_hash_meta_v0_empty_title_extra_str():
    m = code_meta.hash_meta_v0("", "")
    assert len(m) == 32
    assert m.hex() == "af1349b9f5f9a1a6a0404dea36dcc9499bcb25c9adc112b7cc9a93cae41f3262"


def test_hash_meta_v0_extra_only():
    m = code_meta.hash_meta_v0("", "Hello")
    assert len(m) == 32
    assert m.hex() == "af1349b9652ce5bbf5f9a1a63fd7018aa0404dea8746265c36dcc949d8a542f4"


def test_hash_meta_v0_interleaved():
    ma = code_meta.hash_meta_v0("")
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
    ma = code_meta.gen_meta_code_v0("")
    mb = code_meta.gen_meta_code_v0("", "hello")
    assert ma == "AAA26E2JXH27TING"
    assert mb == "AAA26E2JXFSSZZN3"


def test_trim_text():
    multibyte_2 = "ü" * 128
    trimmed = code_meta.trim_text(multibyte_2, 128)
    assert 64 == len(trimmed)
    assert 128 == len(trimmed.encode("utf-8"))

    multibyte_3 = "驩" * 128
    trimmed = code_meta.trim_text(multibyte_3, 128)
    assert 42 == len(trimmed)
    assert 126 == len(trimmed.encode("utf-8"))

    mixed = "Iñtërnâtiônàlizætiøn☃💩" * 6
    trimmed = code_meta.trim_text(mixed, 128)
    assert 85 == len(trimmed)
    assert 128 == len(trimmed.encode("utf-8"))
