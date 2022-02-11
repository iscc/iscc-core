# -*- coding: utf-8 -*-
"""Build conformance `data.json` from `inputs.yaml`"""
import io
from copy import copy

import yaml
import json
import pathlib
import iscc_core
from loguru import logger as log

HERE = pathlib.Path(__file__).parent.absolute()
INPUTS = HERE / "inputs.yaml"
TEST_DATA = HERE / "../iscc_core/data.json"


def dump_compact(data):
    """Dump JSON with maximum depth 4 indent for better readability"""
    depth = 4
    space = " " * 2
    s = json.dumps(data, indent=2, ensure_ascii=False)
    lines = s.splitlines()
    N = len(lines)

    def is_odl(i):
        return i in range(N) and lines[i].startswith(space * (depth + 1))

    def is_obl(i):
        return not is_odl(i) and is_odl(i + 1)

    def is_cbl(i):
        return not is_odl(i) and is_odl(i - 1)

    def shorten_line(line_index):
        if not is_obl(line_index):
            return lines[line_index]
        start = line_index
        end = start
        while not is_cbl(end):
            end += 1
        has_trailing_comma = lines[end][-1] == ","
        _lines = [
            lines[start][-1],
            *lines[start + 1 : end],
            lines[end].replace(",", ""),
        ]
        d = json.dumps(json.loads(" ".join(_lines)), ensure_ascii=False)
        return lines[line_index][:-1] + d + ("," if has_trailing_comma else "")

    s = "\n".join([shorten_line(i) for i in range(N) if not is_odl(i) and not is_cbl(i)])

    return s


def main():
    with open(INPUTS, "rt", encoding="utf-8") as stream:
        data = yaml.safe_load(stream)

    for funcname, tests in data.items():
        for testname, testdata in tests.items():
            func = getattr(iscc_core, funcname)
            args = testdata["inputs"]

            # Convert stream and bytes inputs
            dargs = copy(args)
            nargs = []
            for darg in dargs:
                if isinstance(darg, str) and darg.startswith("stream:"):
                    nargs.append(io.BytesIO(bytes.fromhex(darg.lstrip("stream:"))))
                elif isinstance(darg, str) and darg.startswith("bytes:"):
                    nargs.append(bytes.fromhex(darg.lstrip("bytes:")))
                else:
                    nargs.append(darg)

            try:
                result = func(*nargs)
            except Exception as e:
                log.error(f"{testname}.{funcname} called with {nargs} raised {e}")
                raise

            testdata["outputs"] = result
    with open(TEST_DATA, "w", encoding="utf-8", newline="\n") as outf:
        out_data = dump_compact(data)
        outf.write(out_data)


if __name__ == "__main__":
    main()
