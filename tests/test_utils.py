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
    assert ic.hamming_distance_bytes(A_BYT, B_BYT) == 4


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


def test_ipfs_hash(static_bytes):
    assert (
        ic.ipfs_hash(io.BytesIO(static_bytes))
        == "f0155171c4dda3d7c7b4833d2f73890173860f1e6ab3fa19c4e57b854fc7f960b"
    )


def test_ipfs_hash_raises(static_bytes):
    MB2 = static_bytes + static_bytes
    with pytest.raises(ValueError):
        ic.ipfs_hash(io.BytesIO(MB2))


def test_canonicalize():
    assert ic.json_canonical({"hello": "wörld"}) == b'{"hello":"w\xc3\xb6rld"}'


def test_sliding_window_raises():
    with pytest.raises(AssertionError):
        ic.sliding_window([1, 2, 3, 4, 5], 1)


def test_hamming_distance_raises():
    a, b = os.urandom(8), os.urandom(9)
    with pytest.raises(AssertionError):
        ic.hamming_distance_bytes(a, b)
