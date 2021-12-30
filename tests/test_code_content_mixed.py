# -*- coding: utf-8 -*-
import pytest
import iscc_core


def test_gen_mixed_code_v0_single_raises():
    tc = iscc_core.gen_text_code_v0("Hello World", bits=64)
    with pytest.raises(AssertionError):
        iscc_core.gen_mixed_code_v0([tc.iscc])


def test_gen_mixed_code_v0_non_cc_raises():
    tc = iscc_core.gen_text_code_v0("Hello World", bits=64)
    mc = iscc_core.gen_meta_code_v0("Meta Code Title", bits=64)
    codes = tc.iscc, mc.iscc
    with pytest.raises(AssertionError):
        iscc_core.gen_mixed_code_v0(codes, bits=64)


def test_gen_mixed_code_v0_codes_mixed_length():
    tc_long = iscc_core.gen_text_code_v0("Hello World", bits=256)
    tc_short = iscc_core.gen_text_code_v0("Short Text-Code", bits=64)
    codes = tc_long.iscc, tc_short.iscc
    assert iscc_core.gen_mixed_code_v0(codes=codes, bits=64).dict_raw() == dict(
        iscc="ISCC:EQASB7WL7325X5PW",
        parts=[
            "ISCC:EAD75Q74YXNZC4EKRCQEKOXKMYHCJIUHQNZ3P5FGVJRE4IBHR3F7HRY",
            "ISCC:EAAVUCMGOTFWLZU6",
        ],
    )


def test_gen_mixed_code_v0_codes_to_short_raises():
    tc_long = iscc_core.gen_text_code_v0("Hello World", bits=256)
    tc_short = iscc_core.gen_text_code_v0("Short Text-Code", bits=64)
    codes = tc_long.iscc, tc_short.iscc
    with pytest.raises(AssertionError):
        iscc_core.gen_mixed_code_v0(codes=codes, bits=128)


def test_gen_mixed_code_codes_to_short_raises():
    tc_long = iscc_core.gen_text_code_v0("Hello World", bits=256)
    tc_short = iscc_core.gen_text_code_v0("Short Text-Code", bits=64)
    codes = tc_long.iscc, tc_short.iscc
    with pytest.raises(AssertionError):
        iscc_core.gen_mixed_code(codes=codes, bits=128)
