# -*- coding: utf-8 -*-
import iscc_core
from iscc_core.codec import Code


def test_gen_iscc_id_v0_single_component():
    tc = iscc_core.gen_text_code_v0("Hello World")
    iscc_id = iscc_core.gen_iscc_id(0, tc.code)
    assert iscc_id == "MAACB7WD7TC5XELQ"
    code = Code(iscc_id)
    assert code.explain == "ID-PRIVATE-V0-64-20fec3fcc5db9170"


def test_gen_iscc_id_v0_single_component_uv():
    tc = iscc_core.gen_text_code_v0("Hello World")
    iscc_id = iscc_core.gen_iscc_id(0, tc.code, uc=1)
    assert iscc_id == "MAASB7WD7TC5XELQAE"
    code = Code(iscc_id)
    assert code.explain == "ID-PRIVATE-V0-72-20fec3fcc5db9170-1"


def test_gen_iscc_id_v0_single_component_uv_2byte():
    tc = iscc_core.gen_text_code_v0("Hello World")
    iscc_id = iscc_core.gen_iscc_id(0, tc.code, uc=257)
    assert iscc_id == "MABCB7WD7TC5XELQQEBA"
    code = Code(iscc_id)
    assert code.explain == "ID-PRIVATE-V0-80-20fec3fcc5db9170-257"


def test_gen_iscc_id_v0_multiple_components():
    mc = iscc_core.gen_meta_code_v0("Some Title")
    tc = iscc_core.gen_text_code_v0("Hello World")
    code = mc.code + tc.code
    iscc_id = iscc_core.gen_iscc_id(1, code)
    assert iscc_id == "MEACB7X7777574L6"
    code = Code(iscc_id)
    assert code.explain == "ID-BITCOIN-V0-64-20feffffffdff17e"
