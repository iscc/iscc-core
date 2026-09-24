# -*- coding: utf-8 -*-
"""An application that claims ISCC conformance MUST pass all core functions from the
ISCC conformance test suite. The test suite is available as JSON data on
[GitHub](https://raw.githubusercontent.com/iscc/iscc-core/master/iscc_core/data.json).
Test data is structured as follows:

```json
{
  "_metadata": {
    "generated": "<ISO 8601 UTC timestamp>",
    "generator": "<iscc-core version>",
    "description": "ISCC conformance test data (ISO 24138:2024)"
  },
  "<function_name>": {
    "<test_name>": {
      "inputs": ["<value1>", "<value2>"],
      "outputs": ["value1>", "<value2>"]
      }
   }
}
```

Inputs that are expected to be `raw bytes or byte-streams` are embedded as HEX encoded strings
in JSON and prefixed with `stream:` or `bytes:` to support automated decoding during
implementation testing. Outputs that are raw bytes are embedded the same way with the
`bytes:` prefix.

!!! example
    Byte-stream inputs in JSON test data:
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
import io
from typing import Generator, Tuple, Callable, Any, List
import iscc_core as ic

HERE = pathlib.Path(__file__).parent.absolute()
TEST_DATA = HERE / "data.json"


def _decode_input(value):
    # type: (Any) -> Any
    """Decode a serialized test value: `stream:<hex>` to BytesIO, `bytes:<hex>` to bytes."""
    if isinstance(value, str) and value.startswith("stream:"):
        return io.BytesIO(bytes.fromhex(value.removeprefix("stream:")))
    if isinstance(value, str) and value.startswith("bytes:"):
        return bytes.fromhex(value.removeprefix("bytes:"))
    return value


def conformance_testdata():
    # type: () -> Generator[Tuple[str, Callable, List[Any], List[Any]]]
    """
    Yield tuples of test data.

    :return: Tuple with testdata (test_name, func_obj, inputs, outputs)
    :rtype: Generator[Tuple[str, Callable, List[Any], List[Any]]]
    """
    with open(TEST_DATA, "rb") as stream:
        data = json.load(stream)
    for func_name, tests in data.items():
        if func_name.startswith("_"):
            continue
        func_obj = getattr(ic, func_name)
        for test_name, test_values in tests.items():
            test_values["inputs"] = [_decode_input(tv) for tv in test_values["inputs"]]
            test_values["outputs"] = _decode_input(test_values["outputs"])

            yield test_name, func_obj, test_values["inputs"], test_values["outputs"]


def conformance_selftest():  # pragma: no cover
    # type: () -> bool
    """
    Run conformance tests.

    :return: whether all tests passed
    :rtype: bool
    """
    passed = True
    for test_name, func, inputs, outputs in conformance_testdata():
        try:
            if func(*inputs) != outputs:
                raise AssertionError(f"FAILED: {func.__name__}.{test_name}")
            log.info(f"PASSED: {func.__name__}.{test_name}")
        except Exception as e:
            log.error(f"FAILED: {func.__name__}.{test_name} with {e}")
            passed = False
    return passed
