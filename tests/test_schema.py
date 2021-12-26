# -*- coding: utf-8 -*-
import iscc_core


def test_ISCC_jcs():
    mc = iscc_core.gen_meta_code("Hello", "World")
    assert mc.jcs() == (
        b'{"description":"World",'
        b'"iscc":"AAAWKLHFXNSF7NNE",'
        b'"metahash":"bf73d18575a736e4037d45f9e316085b86c19be6363de6aa789e13deaacc1c4e",'
        b'"name":"Hello"}'
    )


def test_ISCC_ipfs_hash():
    mc = iscc_core.gen_meta_code("Hello", "World")
    assert (
        mc.ipfs_hash()
        == "f0155171c6e0dd159a3da1a6c2516d813d9bfa727155392571d785c6c8489df1b"
    )
