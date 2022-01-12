# -*- coding: utf-8 -*-
import io
import iscc_core


def test_gen_iscc_id_v0_single_component():
    tc = iscc_core.gen_text_code_v0("Hello World")
    iscc_id = iscc_core.gen_iscc_id(0, tc.iscc)
    assert iscc_id.iscc == "ISCC:MAACAJINXFXA2SQX"
    assert iscc_id.code_obj.explain == "ID-PRIVATE-V0-64-20250db96e0d4a17"


def test_gen_iscc_id_v0_single_component_uc():
    tc = iscc_core.gen_text_code_v0("Hello World")
    iscc_id = iscc_core.gen_iscc_id(0, tc.iscc, uc=1)
    assert iscc_id.iscc == "ISCC:MAASAJINXFXA2SQXAE"
    assert iscc_id.code_obj.explain == "ID-PRIVATE-V0-72-20250db96e0d4a17-1"


def test_gen_iscc_id_v0_single_component_uc_2byte():
    tc = iscc_core.gen_text_code_v0("Hello World")
    iscc_id = iscc_core.gen_iscc_id(0, tc.iscc, uc=257)
    assert iscc_id.iscc == "ISCC:MABCAJINXFXA2SQXQEBA"
    assert iscc_id.code_obj.explain == "ID-PRIVATE-V0-80-20250db96e0d4a17-257"


def test_gen_iscc_id_v0_multiple_components():
    mc = iscc_core.gen_meta_code_v0("Some Title")
    tc = iscc_core.gen_text_code_v0("Hello World")
    code = mc.code + tc.code
    iscc_id = iscc_core.gen_iscc_id(1, code)
    assert iscc_id.iscc == "ISCC:MEACAJJ5757U72R7"
    assert iscc_id.code_obj.explain == "ID-BITCOIN-V0-64-20253dff7f4fea3f"


def test_gen_iscc_id_v0_instance_only():
    ic = iscc_core.gen_instance_code_v0(io.BytesIO(b"hello world"))
    iscc_id = iscc_core.gen_iscc_id(0, ic.iscc)
    assert iscc_id.iscc == "ISCC:MAAEBV2JQHX2OCQM"
    assert iscc_id.code_obj.explain == "ID-PRIVATE-V0-64-40d74981efa70a0c"


def test_gen_iscc_id_v0_data_instance():
    ic = iscc_core.gen_instance_code_v0(io.BytesIO(b"hello world"))
    dc = iscc_core.gen_data_code_v0(io.BytesIO(b"hello world"))
    iscc_sum = iscc_core.gen_iscc_code_v0([ic.iscc, dc.iscc])
    iscc_id = iscc_core.gen_iscc_id(0, iscc_sum.iscc)
    assert iscc_id.iscc == "ISCC:MAADB7WD7TC5XELQ"
    assert iscc_id.code_obj.explain == "ID-PRIVATE-V0-64-30fec3fcc5db9170"


def test_incr_iscc_id():
    assert iscc_core.iscc_id.incr_iscc_id("MAADB7WD7TC5XELQ") == "MAADB7WD7TC5XELQAE"


def test_incr_iscc_id_explain():
    incr = iscc_core.iscc_id.incr_iscc_id("MAADB7WD7TC5XELQ")
    assert iscc_core.codec.Code(incr).explain == "ID-PRIVATE-V0-64-30fec3fcc5db9170-1"


def test_incr_iscc_id_v0():
    assert iscc_core.iscc_id.incr_iscc_id_v0("MAADB7WD7TC5XELQ") == "MAADB7WD7TC5XELQAE"
    assert (
        iscc_core.codec.Code("MAADB7WD7TC5XELQAE").explain
        == "ID-PRIVATE-V0-64-30fec3fcc5db9170-1"
    )
    assert (
        iscc_core.iscc_id.incr_iscc_id_v0("MAADB7WD7TC5XELQAE") == "MAADB7WD7TC5XELQAI"
    )
