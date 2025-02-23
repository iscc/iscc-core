"""Arbitrary Sequences of ISCC-UNITs"""

import os
from io import BytesIO

import iscc_core as ic


def decompose_64():
    """Decompose a sequence of 64-bit ISCC Units"""
    data = os.urandom(1024)
    data_code = ic.gen_data_code_v0(BytesIO(data), bits=64)
    inst_code = ic.gen_instance_code(BytesIO(data), bits=64)
    print(f"DATA-UNIT: {data_code}")
    print(f"INST-UNIT: {inst_code}")
    sequenced = (
        "ISCC:" + data_code["iscc"].replace("ISCC:", "") + inst_code["iscc"].replace("ISCC:", "")
    )
    print(f"SEQUENCED-UNITS: {sequenced}")
    print(ic.iscc_decompose(sequenced))


def decompose_128():
    """Decompose a sequence of 128-bit ISCC Units"""
    data = os.urandom(1024)
    data_code = ic.gen_data_code_v0(BytesIO(data), bits=128)
    inst_code = ic.gen_instance_code(BytesIO(data), bits=128)
    print(f"DATA-UNIT: {data_code}")
    print(f"INST-UNIT: {inst_code}")
    sequenced = (
        "ISCC:" + data_code["iscc"].replace("ISCC:", "") + inst_code["iscc"].replace("ISCC:", "")
    )
    print(f"SEQUENCED-UNITS: {sequenced}")
    print(ic.iscc_decompose(sequenced))


if __name__ == "__main__":
    decompose_64()
    decompose_128()
