# -*- coding: utf-8 -*-
import io
import pytest
import iscc_core as ic

wallet = "1Bq568oLhi5HvdgC6rcBSGmu4G3FeAntCz"


def test_gen_iscc_id_v0_single_component():
    tc = ic.gen_text_code_v0("Hello World")
    iscc_id = ic.gen_iscc_id(tc["iscc"], chain_id=0, wallet=wallet)
    assert iscc_id == {"iscc": "ISCC:MAAJU3Y6GCTXLVKA"}
    assert ic.iscc_explain(iscc_id["iscc"]) == "ID-PRIVATE-V0-64-9a6f1e30a775d540"


def test_gen_iscc_id_v0_single_component_uc():
    tc = ic.gen_text_code_v0("Hello World")
    iscc_id = ic.gen_iscc_id(tc["iscc"], chain_id=0, wallet=wallet, uc=1)
    assert iscc_id == {"iscc": "ISCC:MAAZU3Y6GCTXLVKAAE"}
    assert ic.iscc_explain(iscc_id["iscc"]) == "ID-PRIVATE-V0-72-9a6f1e30a775d540-1"


def test_gen_iscc_id_v0_single_component_uc_2byte():
    tc = ic.gen_text_code_v0("Hello World")
    iscc_id = ic.gen_iscc_id(tc["iscc"], 0, wallet=wallet, uc=257)
    assert iscc_id["iscc"] == "ISCC:MABJU3Y6GCTXLVKAQEBA"
    assert ic.iscc_explain(iscc_id["iscc"]) == "ID-PRIVATE-V0-80-9a6f1e30a775d540-257"


def test_gen_iscc_id_v0_multiple_components():
    mc = ic.gen_meta_code_v0("Some Title")["iscc"]
    tc = ic.gen_text_code_v0("Hello World")["iscc"]
    code = ic.iscc_clean(mc) + ic.iscc_clean(tc)
    iscc_id = ic.gen_iscc_id(iscc_code=code, chain_id=1, wallet=wallet)
    assert iscc_id["iscc"] == "ISCC:MEAJU7YOOSTOPYLI"
    assert ic.iscc_explain(iscc_id["iscc"]) == "ID-BITCOIN-V0-64-9a7f0e74a6e7e168"


def test_gen_iscc_id_v0_full_code():
    iscc_code = "ISCC:KQDZJFP6WBM3IIFZ7CRXCNDCNUU3ZEWGL5HAKHNMYHLN2WULPN3ZFHJO7AUS6VQQVM7Q"
    iscc_id = ic.gen_iscc_id(iscc_code=iscc_code, chain_id=1, wallet=wallet)
    assert iscc_id["iscc"] == "ISCC:MEAI5HGE6Z3QHYX7"


def test_gen_iscc_id_v0_instance_only():
    icode = ic.gen_instance_code_v0(io.BytesIO(b"hello world"))
    iscc_id = ic.gen_iscc_id(icode["iscc"], chain_id=0, wallet=wallet)
    assert iscc_id["iscc"] == "ISCC:MAAPVHK2BATN7FK3"
    assert ic.iscc_explain(iscc_id["iscc"]) == "ID-PRIVATE-V0-64-fa9d5a0826df955b"


def test_gen_iscc_id_v0_data_instance():
    icode = ic.gen_instance_code_v0(io.BytesIO(b"hello world"))
    dc = ic.gen_data_code_v0(io.BytesIO(b"hello world"))
    iscc_sum = ic.gen_iscc_code_v0([icode["iscc"], dc["iscc"]])
    iscc_id = ic.gen_iscc_id(iscc_sum["iscc"], chain_id=0, wallet=wallet)
    assert iscc_id["iscc"] == "ISCC:MAAIVNGQOUGKGDRH"
    assert ic.iscc_explain(iscc_id["iscc"]) == "ID-PRIVATE-V0-64-8ab4d0750ca30e27"


def test_incr_iscc_id():
    assert ic.iscc_id.iscc_id_incr("MAADB7WD7TC5XELQ") == "MAADB7WD7TC5XELQAE"


def test_incr_iscc_id_explain():
    incr = ic.iscc_id.iscc_id_incr("MAADB7WD7TC5XELQ")
    assert ic.Code(incr).explain == "ID-PRIVATE-V0-64-30fec3fcc5db9170-1"


def test_incr_iscc_id_v0():
    assert ic.iscc_id.iscc_id_incr_v0("MAADB7WD7TC5XELQ") == "MAADB7WD7TC5XELQAE"
    assert ic.Code("MAADB7WD7TC5XELQAE").explain == "ID-PRIVATE-V0-64-30fec3fcc5db9170-1"
    assert ic.iscc_id.iscc_id_incr_v0("MAADB7WD7TC5XELQAE") == "MAADB7WD7TC5XELQAI"


def test_incr_iscc_id_v0_raises_wrong_mt():
    mc = ic.Code.rnd(ic.MT.META).code
    with pytest.raises(AssertionError):
        ic.iscc_id_incr_v0(mc)


def test_incr_iscc_id_v0_raises_wrong_vs():
    mc = ic.Code.rnd(ic.MT.ID)
    head = list(mc._head)
    head[2] = 1
    mc._head = tuple(head)
    with pytest.raises(AssertionError):
        ic.iscc_id_incr_v0(mc.code)


def test_gen_iscc_id_v0_raises_chain_id():
    code = ic.Code.rnd(ic.MT.ISCC, bits=256)
    with pytest.raises(AssertionError):
        ic.gen_iscc_id_v0(code.code, 5, wallet=wallet)


def test_alg_simhash_from_iscc_id():
    shash = ic.alg_simhash_from_iscc_id("MAAJU3Y6GCTXLVKA", wallet=wallet)
    assert shash == "20250db96e0d4a17"
