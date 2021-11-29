# -*- coding: utf-8 -*-
import iscc_core as ic


def test_gen_iscc_code_v0():
    mid = ic.Code.rnd(ic.MT.META, 64)
    cid = ic.Code.rnd(ic.MT.CONTENT, 64)
    did = ic.Code.rnd(ic.MT.DATA, 128)
    iid = ic.Code.rnd(ic.MT.INSTANCE, 256)
    icode = ic.gen_iscc_code_v01([mid, cid, did, iid])
    assert icode.maintype == ic.MT.ISCC
    assert icode.length == 256
    assert icode.explain.startswith("ISCC-")
    assert ic.gen_iscc_code_v01([did, mid, cid, iid]) == icode


def test_gen_iscc_code_v0_body():
    data = b"\x00" * 8
    mid = ic.Code.rnd(ic.MT.META, data=data)
    cid = ic.Code.rnd(ic.MT.CONTENT, data=data)
    did = ic.Code.rnd(ic.MT.DATA, data=data)
    iid = ic.Code.rnd(ic.MT.INSTANCE, data=data)
    icode = ic.gen_iscc_code_v01([mid, cid, did, iid])
    assert icode.hash_bytes == data * 4
