# -*- coding: utf-8 -*-
"""Run conformance tests"""
import pytest
import json
import pathlib
import iscc_core


HERE = pathlib.Path(__file__).parent.absolute()
TEST_DATA = HERE / "../iscc_core/data.json"


def read_test_data():
    with open(TEST_DATA, "rb") as stream:
        data = json.load(stream)
    flat = []
    for func_name, tests in data.items():
        func_obj = getattr(iscc_core, func_name)
        for test_name, test_values in tests.items():
            flat.append((func_obj, test_values["inputs"], test_values["outputs"]))
    return flat


@pytest.mark.parametrize("function,inputs,outputs", read_test_data())
def test_conformance(function, inputs, outputs):
    assert function(*inputs).dict(exclude_unset=True, exclude_none=True) == outputs
