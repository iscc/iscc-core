# -*- coding: utf-8 -*-
from iscc_core import codec as c
from iscc_core import gen_iscc_code_v01


def test_gen_iscc_code_v0():
    mid = c.Code.rnd(c.MT.META, 64)
    cid = c.Code.rnd(c.MT.CONTENT, 64)
    did = c.Code.rnd(c.MT.DATA, 128)
    iid = c.Code.rnd(c.MT.INSTANCE, 256)
    icode = gen_iscc_code_v01([mid, cid, did, iid])
    assert icode.maintype == c.MT.ISCC
    assert icode.length == 256
    assert icode.explain.startswith("ISCC-")
    assert gen_iscc_code_v01([did, mid, cid, iid]) == icode


def test_gen_iscc_code_v0_body():
    data = b"\x00" * 8
    mid = c.Code.rnd(c.MT.META, data=data)
    cid = c.Code.rnd(c.MT.CONTENT, data=data)
    did = c.Code.rnd(c.MT.DATA, data=data)
    iid = c.Code.rnd(c.MT.INSTANCE, data=data)
    icode = gen_iscc_code_v01([mid, cid, did, iid])
    assert icode.hash_bytes == data * 4
