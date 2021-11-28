# -*- coding: utf-8 -*-
import iscc_core


def test_gen_iscc_id_v0_single_component():
    tc = iscc_core.gen_text_code_v0("Hello World")
    iscc_id = iscc_core.gen_iscc_id(0, tc.code)
    assert iscc_id == "MAACB7WD7TC5XELQ"
    code = iscc_core.Code(iscc_id)
    assert code.explain == "ID-PRIVATE-V0-64-20fec3fcc5db9170"


def test_gen_iscc_id_v0_single_component_uv():
    tc = iscc_core.gen_text_code_v0("Hello World")
    iscc_id = iscc_core.gen_iscc_id(0, tc.code, uc=1)
    assert iscc_id == "MAASB7WD7TC5XELQAE"
    code = iscc_core.Code(iscc_id)
    assert code.explain == "ID-PRIVATE-V0-72-20fec3fcc5db917001"


def test_gen_iscc_id_v0_multiple_components():
    mc = iscc_core.gen_meta_code_v0("Some Title")
    tc = iscc_core.gen_text_code_v0("Hello World")
    code = mc.code + tc.code
    iscc_id = iscc_core.gen_iscc_id(1, code)
    assert iscc_id == "MEACB7X7777574L6"
    code = iscc_core.Code(iscc_id)
    assert code.explain == "ID-BITCOIN-V0-64-20feffffffdff17e"
