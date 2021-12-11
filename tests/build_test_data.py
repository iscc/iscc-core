# -*- coding: utf-8 -*-
"""Build conformance `data.json` from `inputs.yaml`"""
import yaml
import json
import pathlib
import iscc_core
from iscc_core.schema import IsccBase

HERE = pathlib.Path(__file__).parent.absolute()
INPUTS = HERE / "inputs.yaml"
TEST_DATA = HERE / "../iscc_core/data.json"


def main():
    with open(INPUTS, "rt", encoding="utf-8") as stream:
        data = yaml.safe_load(stream)

    for funcname, tests in data.items():
        for testname, testdata in tests.items():
            func = getattr(iscc_core, funcname)
            args = testdata["inputs"]
            result = func(*args)
            if isinstance(result, IsccBase):
                testdata["outputs"] = result.dict(exclude_unset=True, exclude_none=True)
            else:
                testdata["outputs"] = result
    with open(TEST_DATA, "w", encoding="utf-8") as outf:
        json.dump(data, outf, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    main()
