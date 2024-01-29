# -*- coding: utf-8 -*-
"""Run conformance tests"""
from typing import Generator
import pytest
from iscc_core import conformance
from iscc_core.__main__ import selftest


def test_generate_tests():
    test_generator = conformance.conformance_testdata()
    assert isinstance(test_generator, Generator)


def test_selftest():
    assert selftest() is True


def test_confromance_selftest():
    assert conformance.conformance_selftest()


@pytest.mark.parametrize("testname,function,inputs,outputs", conformance.conformance_testdata())
def test_conformance(testname, function, inputs, outputs):
    result = function(*inputs)
    if hasattr(result, "dict"):
        assert result.dict() == outputs, f"FAILED {testname}"
    else:
        assert result == outputs
