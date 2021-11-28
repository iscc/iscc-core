# -*- coding: utf-8 -*-
import pytest
import iscc_core


def test_gen_mixed_code_single_raises():
    tc = iscc_core.gen_text_code_v0("Hello World", bits=64)
    with pytest.raises(AssertionError):
        iscc_core.gen_mixed_code_v0([tc.code])


def test_gen_mixed_code_non_cc_raises():
    tc = iscc_core.gen_text_code_v0("Hello World", bits=64)
    mc = iscc_core.gen_meta_code_v0("Meta Code Title", bits=64)
    codes = tc.code, mc.code
    with pytest.raises(AssertionError):
        iscc_core.gen_mixed_code_v0(codes, bits=64)


def test_gen_mixed_code_codes_mixed_length():
    tc_long = iscc_core.gen_text_code_v0("Hello World", bits=256)
    tc_short = iscc_core.gen_text_code_v0("Short Text-Code", bits=64)
    codes = tc_long.code, tc_short.code
    assert iscc_core.gen_mixed_code_v0(codes=codes, bits=64) == dict(
        code="EQASB7WL7325X5PW",
        title=None,
        parts=["EAA75Q74YXNZC4EK", "EAAVUCMGOTFWLZU6"],
    )


def test_gen_mixed_code_codes_to_short_raises():
    tc_long = iscc_core.gen_text_code_v0("Hello World", bits=256)
    tc_short = iscc_core.gen_text_code_v0("Short Text-Code", bits=64)
    codes = tc_long.code, tc_short.code
    with pytest.raises(AssertionError):
        iscc_core.gen_mixed_code_v0(codes=codes, bits=128)
