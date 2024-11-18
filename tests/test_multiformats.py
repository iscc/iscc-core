# -*- coding: utf-8 -*-
import iscc_core as ic

CANONICAL = "ISCC:EAAWFH3PX3MCYB6N"
MF_B32H = "vpg0i00b2jtnrtm1c0v6g"
MF_B32H_P = "iscc:vpg0i00b2jtnrtm1c0v6g"
ISCC_OBJ = ic.Code(CANONICAL)


def test_iscc_clean():
    assert ic.iscc_clean(MF_B32H) == MF_B32H
    assert ic.iscc_clean(MF_B32H_P) == MF_B32H


def test_iscc_decode():
    assert ic.iscc_decode(MF_B32H) == ISCC_OBJ._head + (ISCC_OBJ._body.tobytes(),)
    assert ic.iscc_decode(MF_B32H_P) == ISCC_OBJ._head + (ISCC_OBJ._body.tobytes(),)


def test_iscc_decompose():
    decomposed = ic.iscc_decompose(ISCC_OBJ.uri)
    assert ic.iscc_decompose(MF_B32H) == decomposed
    assert ic.iscc_decompose(MF_B32H_P) == decomposed
