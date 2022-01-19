# -*- coding: utf-8 -*-
import io
import iscc_core as ic


def test_gen_iscc_id_v0_single_component():
    tc = ic.gen_text_code_v0("Hello World")
    iscc_id = ic.gen_iscc_id(0, tc["iscc"])
    assert iscc_id == {"iscc": "ISCC:MAACAJINXFXA2SQX"}
    assert ic.explain(iscc_id["iscc"]) == "ID-PRIVATE-V0-64-20250db96e0d4a17"


def test_gen_iscc_id_v0_single_component_uc():
    tc = ic.gen_text_code_v0("Hello World")
    iscc_id = ic.gen_iscc_id(0, tc["iscc"], uc=1)
    assert iscc_id == {"iscc": "ISCC:MAASAJINXFXA2SQXAE"}
    assert ic.explain(iscc_id["iscc"]) == "ID-PRIVATE-V0-72-20250db96e0d4a17-1"


def test_gen_iscc_id_v0_single_component_uc_2byte():
    tc = ic.gen_text_code_v0("Hello World")
    iscc_id = ic.gen_iscc_id(0, tc["iscc"], uc=257)
    assert iscc_id["iscc"] == "ISCC:MABCAJINXFXA2SQXQEBA"
    assert ic.explain(iscc_id["iscc"]) == "ID-PRIVATE-V0-80-20250db96e0d4a17-257"


def test_gen_iscc_id_v0_multiple_components():
    mc = ic.gen_meta_code_v0("Some Title")["iscc"]
    tc = ic.gen_text_code_v0("Hello World")["iscc"]
    code = ic.clean(mc) + ic.clean(tc)
    iscc_id = ic.gen_iscc_id(1, code)
    assert iscc_id["iscc"] == "ISCC:MEACANI57VXZ67R7"
    assert ic.explain(iscc_id["iscc"]) == "ID-BITCOIN-V0-64-20351dfd6f9f7e3f"


def test_gen_iscc_id_v0_instance_only():
    icode = ic.gen_instance_code_v0(io.BytesIO(b"hello world"))
    iscc_id = ic.gen_iscc_id(0, icode["iscc"])
    assert iscc_id["iscc"] == "ISCC:MAAEBV2JQHX2OCQM"
    assert ic.explain(iscc_id["iscc"]) == "ID-PRIVATE-V0-64-40d74981efa70a0c"


def test_gen_iscc_id_v0_data_instance():
    icode = ic.gen_instance_code_v0(io.BytesIO(b"hello world"))
    dc = ic.gen_data_code_v0(io.BytesIO(b"hello world"))
    iscc_sum = ic.gen_iscc_code_v0([icode["iscc"], dc["iscc"]])
    iscc_id = ic.gen_iscc_id(0, iscc_sum["iscc"])
    assert iscc_id["iscc"] == "ISCC:MAADB7WD7TC5XELQ"
    assert ic.explain(iscc_id["iscc"]) == "ID-PRIVATE-V0-64-30fec3fcc5db9170"


def test_incr_iscc_id():
    assert ic.iscc_id.incr_iscc_id("MAADB7WD7TC5XELQ") == "MAADB7WD7TC5XELQAE"


def test_incr_iscc_id_explain():
    incr = ic.iscc_id.incr_iscc_id("MAADB7WD7TC5XELQ")
    assert ic.Code(incr).explain == "ID-PRIVATE-V0-64-30fec3fcc5db9170-1"


def test_incr_iscc_id_v0():
    assert ic.iscc_id.incr_iscc_id_v0("MAADB7WD7TC5XELQ") == "MAADB7WD7TC5XELQAE"
    assert ic.Code("MAADB7WD7TC5XELQAE").explain == "ID-PRIVATE-V0-64-30fec3fcc5db9170-1"
    assert ic.iscc_id.incr_iscc_id_v0("MAADB7WD7TC5XELQAE") == "MAADB7WD7TC5XELQAI"
