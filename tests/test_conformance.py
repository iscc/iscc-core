# -*- coding: utf-8 -*-
"""Run conformance tests"""
import io
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

            # create byte-stream from first argument strings that start with `stream:`:
            if isinstance(test_values["inputs"][0], str) and test_values["inputs"][
                0
            ].startswith("stream:"):
                test_values["inputs"][0] = io.BytesIO(
                    bytes.fromhex(test_values["inputs"][0].lstrip("stream:"))
                )

            flat.append((func_obj, test_values["inputs"], test_values["outputs"]))
    return flat


@pytest.mark.parametrize("function,inputs,outputs", read_test_data())
def test_conformance(function, inputs, outputs):
    assert function(*inputs).dict(exclude_unset=True, exclude_none=True) == outputs
