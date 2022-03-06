# -*- coding: utf-8 -*-
import pytest
from iscc_schema import IsccMeta

import iscc_core


def test_gen_mixed_code_v0_single_raises():
    tc = iscc_core.gen_text_code_v0("Hello World", bits=64)
    with pytest.raises(AssertionError):
        iscc_core.gen_mixed_code_v0([tc["iscc"]])


def test_gen_mixed_code_v0_non_cc_raises():
    tc = iscc_core.gen_text_code_v0("Hello World", bits=64)["iscc"]
    mc = iscc_core.gen_meta_code_v0("Meta Code Title", bits=64)["iscc"]
    codes = tc, mc
    with pytest.raises(AssertionError):
        iscc_core.gen_mixed_code_v0(codes, bits=64)


def test_gen_mixed_code_v0_codes_mixed_length():
    tc_long = iscc_core.gen_text_code_v0("Hello World", bits=256)["iscc"]
    tc_short = iscc_core.gen_text_code_v0("Short Text-Code", bits=64)["iscc"]
    codes = tc_long, tc_short
    assert iscc_core.gen_mixed_code_v0(codes=codes, bits=64) == {
        "iscc": "ISCC:EQASBPL7XH763357",
        "parts": [
            "ISCC:EADSKDNZNYGUUF5AMFEJLZ5P66CP5YKCOA3X7F36RWE4CIRCBTUWXYY",
            "ISCC:EAA3265Q67Q27P7F",
        ],
    }


def test_gen_mixed_code_v0_codes_to_short_raises():
    tc_long = iscc_core.gen_text_code_v0("Hello World", bits=256)["iscc"]
    tc_short = iscc_core.gen_text_code_v0("Short Text-Code", bits=64)["iscc"]
    codes = tc_long, tc_short
    with pytest.raises(AssertionError):
        iscc_core.gen_mixed_code_v0(codes=codes, bits=128)


def test_gen_mixed_code_codes_to_short_raises():
    tc_long = iscc_core.gen_text_code_v0("Hello World", bits=256)["iscc"]
    tc_short = iscc_core.gen_text_code_v0("Short Text-Code", bits=64)["iscc"]
    codes = tc_long, tc_short
    with pytest.raises(AssertionError):
        iscc_core.gen_mixed_code(codes=codes, bits=128)


def test_gen_mixed_code_schema_conformance():
    tc_long = iscc_core.gen_text_code_v0("Hello World", bits=256)["iscc"]
    tc_short = iscc_core.gen_text_code_v0("Short Text-Code", bits=64)["iscc"]
    codes = tc_long, tc_short
    iscc_obj = IsccMeta(**iscc_core.gen_mixed_code_v0(codes=codes))
    assert iscc_obj.iscc == "ISCC:EQASBPL7XH763357"
