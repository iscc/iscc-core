# -*- coding: utf-8 -*-
import pytest
import iscc_core as ic


def test_minhash_empty():
    with pytest.raises(ValueError):
        ic.alg_minhash([])


def test_minhash_single_feature():
    mh = ic.alg_minhash([2**16])
    assert isinstance(mh, list)
    assert len(mh) == 64
    assert mh[0] == 1968499307
    assert mh[-1] == 2739100501


def test_minhash_32bit_features():
    i32 = 2**32 - 1
    mh = ic.alg_minhash([2**64 - 1])
    for n in mh:
        assert n <= i32


def test_minhash_compress():
    mh = ic.alg_minhash([2**16])
    digest = ic.alg_minhash_compress(mh)
    assert len(digest) == 32
    assert digest.hex() == "a18e2fb2bd663d21db9c7dcc9ae78380253cae5bf089766d87a6b51fcb3f8f8e"
    mh = [0b10100001, 0b11000010, 0b10110100, 0b10011000]
    compressed = ic.alg_minhash_compress(mh)
    as_int = int.from_bytes(compressed, "big", signed=False)
    assert as_int == 0b1000_0100_0010_0001


def test_minhash_64():
    mh = ic.alg_minhash_64([2**16])
    assert mh.hex() == "a18e2fb2bd663d21"
