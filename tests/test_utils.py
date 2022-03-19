# -*- coding: utf-8 -*-
import io
import os

import pytest
import iscc_core as ic


A_INT = 0b00000000_00001111_00000000_00000000_00000000_00000000_00000000_00000000
B_INT = 0b11110000_00001111_00000000_00000000_00000000_00000000_00000000_00000000
A_BYT = A_INT.to_bytes(length=8, byteorder="big", signed=False)
B_BYT = B_INT.to_bytes(length=8, byteorder="big", signed=False)


def test_hamming_distance():
    assert ic.iscc_distance_bytes(A_BYT, B_BYT) == 4


def test_similarity_single_64():
    ia = ic.Code.rnd(mt=ic.MT.CONTENT, st=ic.ST_ISCC.IMAGE, bits=64, data=A_BYT).code
    ib = ic.Code.rnd(mt=ic.MT.CONTENT, st=ic.ST_ISCC.IMAGE, bits=64, data=B_BYT).code
    assert ic.iscc_similarity(ia, ib) == 93


def test_similarity_single_256():
    a = "AAD7SATLZUS57KXZZL2HXAD7HT6264AHEIRZQ4QTLB6LHVRXNTLE7MA"
    b = "AAD7CATK5QX46LX5YL2HXIH7FT626UAHE4RYC4QTDB6LXVRXNDJE7MA"
    assert ic.iscc_similarity(a, b) == 90


def test_similarity_composite():
    a = "KQD7SATLZUS57KXZN2N6SA6A3THBJRQW4B5CZPGWU2PR566ZQNLM2AA"
    b = "KQD7CATK5QX46LX5N2N6SA6A3THBJRQW4B5CZPGWU2PR566ZQNLM2AA"
    assert ic.iscc_similarity(a, b) == 96


def test_distance_single_64():
    ia = ic.Code.rnd(mt=ic.MT.CONTENT, st=ic.ST_ISCC.IMAGE, bits=64, data=A_BYT).code
    ib = ic.Code.rnd(mt=ic.MT.CONTENT, st=ic.ST_ISCC.IMAGE, bits=64, data=B_BYT).code
    assert ic.iscc_distance(ia, ib) == 4


def test_distance_single_256():
    a = "AAD7SATLZUS57KXZZL2HXAD7HT6264AHEIRZQ4QTLB6LHVRXNTLE7MA"
    b = "AAD7CATK5QX46LX5YL2HXIH7FT626UAHE4RYC4QTDB6LXVRXNDJE7MA"
    assert ic.iscc_distance(a, b) == 24


def test_distance_composite():
    a = "KQD7SATLZUS57KXZN2N6SA6A3THBJRQW4B5CZPGWU2PR566ZQNLM2AA"
    b = "KQD7CATK5QX46LX5N2N6SA6A3THBJRQW4B5CZPGWU2PR566ZQNLM2AA"
    assert ic.iscc_distance(a, b) == 10


def test_sliding_window():
    assert list(ic.utils.sliding_window("", width=4)) == [""]
    assert list(ic.utils.sliding_window("A", width=4)) == ["A"]
    assert list(ic.utils.sliding_window("Hello", width=4)) == ["Hell", "ello"]
    words = ("lorem", "ipsum", "dolor", "sit", "amet")
    slices = list(ic.utils.sliding_window(words, 2))
    assert slices[0] == ("lorem", "ipsum")
    assert slices[1] == ("ipsum", "dolor")
    assert slices[-1] == ("sit", "amet")


def test_sliding_window_retains_sequence_type():
    tuple_sequence = ("lorem", "ipsum", "dolor", "sit", "amet")
    slices = list(ic.utils.sliding_window(tuple_sequence, 2))
    assert isinstance(slices[0], tuple)

    list_sequence = list(tuple_sequence)
    slices = list(ic.utils.sliding_window(list_sequence, 2))
    assert isinstance(slices[0], list)

    text_sequence = "lorem"
    slices = list(ic.utils.sliding_window(text_sequence, 2))
    assert isinstance(slices[0], str)
    assert slices[0] == "lo"
    assert slices[1] == "or"
    assert slices[-1] == "em"


def test_sliding_window_bigger_than_sequence():
    words = ("lorem", "ipsum", "dolor", "sit", "amet")
    slices = list(ic.utils.sliding_window(words, 6))
    assert slices[0] == words

    slices = list(ic.utils.sliding_window("hello", 5))
    assert slices[0] == "hello"


def test__safe_unpack():
    a = ic.Code.rnd(ic.MT.META, bits=64).code
    b = ic.Code.rnd(ic.MT.DATA, bits=64).code
    with pytest.raises(ValueError):
        ic.utils.iscc_pair_unpack(a, b)


def test_cidv1_hex_stream():
    assert (
        ic.cidv1_hex(io.BytesIO(b"hello world"))
        == "f01551220b94d27b9934d3e08a52e52d7da7dabfac484efe37a5380ee9088f7ace2efcde9"
    )


def test_cidv1_hex_bytes():
    assert (
        ic.cidv1_hex(b"hello world")
        == "f01551220b94d27b9934d3e08a52e52d7da7dabfac484efe37a5380ee9088f7ace2efcde9"
    )


def test_hash_ipfs_cidv1_max(static_bytes):
    data = static_bytes[:262144]
    assert (
        ic.cidv1_hex(io.BytesIO(data))
        == "f01551220dd8186a3d57826d3179717fbcaef8e4c24c5380f0ee7d869f41f727015fe17ab"
    )


def test_cidv1_to_token_id():
    token_id = ic.cidv1_to_token_id(
        "f01551220dd8186a3d57826d3179717fbcaef8e4c24c5380f0ee7d869f41f727015fe17ab"
    )
    assert token_id <= 2**256 - 1
    assert (
        token_id == 100189992059221005740937582782800178391670948768450295424002582041064650971051
    )


def test_cidv1_to_token_id_raises():
    with pytest.raises(ValueError):
        ic.cidv1_to_token_id("bafkrei...")
    with pytest.raises(ValueError):
        ic.cidv1_to_token_id(
            "f02551220b94d27b9934d3e08a52e52d7da7dabfac484efe37a5380ee9088f7ace2efcde9"
        )
    with pytest.raises(ValueError):
        ic.cidv1_to_token_id(
            "f01551220b94d27b9934d3e08a52e52d7da7dabfac484efe37a5380ee9088f7ace2efcd"
        )


def test_cidv1_from_token_id():
    cidv1 = ic.cidv1_from_token_id(
        100189992059221005740937582782800178391670948768450295424002582041064650971051
    )
    assert cidv1 == "f01551220dd8186a3d57826d3179717fbcaef8e4c24c5380f0ee7d869f41f727015fe17ab"


def test_hash_ipfs_cidv1_raises(static_bytes):
    data = static_bytes[:262145]
    with pytest.raises(ValueError):
        ic.cidv1_hex(io.BytesIO(data))


def test_canonicalize():
    value = {"hello": "world"}
    assert ic.json_canonical(value) == b'{"hello":"world"}'


def test_canonicalize_non_ascii():
    value = {"hello": "wörld"}
    assert ic.json_canonical(value) == b'{"hello":"w\xc3\xb6rld"}'


def test_canonicalize_small_int():
    value = {"num": 2**52}
    assert ic.json_canonical(value) == b'{"num":4503599627370496}'


def test_canonicalize_large_int():
    value = {"num": 2**53}
    assert ic.json_canonical(value) == b'{"num":9007199254740992}'
    with pytest.raises(ValueError):
        value = {"num": 2**53 + 1}
        ic.json_canonical(value)


def test_sliding_window_raises():
    with pytest.raises(AssertionError):
        ic.sliding_window([1, 2, 3, 4, 5], 1)


def test_hamming_distance_raises():
    a, b = os.urandom(8), os.urandom(9)
    with pytest.raises(AssertionError):
        ic.iscc_distance_bytes(a, b)


def test_multi_hash_blake3():
    assert ic.multi_hash_blake3(b"") == (
        "1e20af1349b9f5f9a1a6a0404dea36dcc9499bcb25c9adc112b7cc9a93cae41f3262"
    )
    assert ic.multi_hash_blake3(b"hello world") == (
        "1e20d74981efa70a0c880b8d8c1985d075dbcbf679b99a5f9914e5aaf96b831a9e24"
    )
