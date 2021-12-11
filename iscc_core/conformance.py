# -*- coding: utf-8 -*-
"""
# Conformance Testing

An application that claims ISCC conformance MUST pass all core functions from the
ISCC conformance test suite. The test suite is available as JSON data on
[Github](https://raw.githubusercontent.com/iscc/iscc-core/master/iscc_core/data.json).
Test data is structured as follows:

```json
{
  "<function_name>": {
    "<test_name>": {
      "inputs": ["<value1>", "<value2>"],
      "outputs": ["value1>", "<value2>"]
      }
   }
}
```

Inputs that are expected to be `raw byte streams` are embedded as HEX encoded strings
in JSON and prefixed with  `stream:` to support automated decoding during
implementation testing.

!!! example
    Byte outputs in JSON test data:
    ```json
    "gen_data_code_v0": {
      "test_0000_two_bytes_64": {
        "inputs": [
          "stream:ff00",
          64
        ],
        "outputs": {
          "iscc": "GAAXL2XYM5BQIAZ3"
        }
      },
      ...
    ```
"""
from loguru import logger as log
import pathlib
import json
import iscc_core
import io
from typing import Generator, Tuple, Callable, Any, List

HERE = pathlib.Path(__file__).parent.absolute()
TEST_DATA = HERE / "data.json"


def generate_tests():
    # type: () -> Generator[Tuple[str, Callable, List[Any], List[Any]]]
    """Yield tuples of test data.

    :return: Tuple with testdata (test_name, func_obj, inputs, outputs)
    :rtype: Generator[Tuple[str, Callable, List[Any], List[Any]]]
    """
    with open(TEST_DATA, "rb") as stream:
        data = json.load(stream)
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
            yield test_name, func_obj, test_values["inputs"], test_values["outputs"]


def selftest():
    # type: () -> bool
    """Run conformance tests.

    :return: whether all tests passed
    :rtype: bool
    """
    passed = True
    for test_name, func, inputs, outputs in generate_tests():
        try:
            assert func(*inputs) == outputs
            log.info(f"PASSED: {func.__name__}.{test_name}")
        except Exception as e:
            log.error(f"FAILED: {func.__name__}.{test_name} with {e}")
            passed = False
    return passed


if __name__ == "__main__":
    selftest()
