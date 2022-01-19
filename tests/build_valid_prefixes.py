# -*- coding: utf-8 -*-
"""Build a list of possible base32 encoded ISCC 2-character prefixes for validation"""
import iscc_core as ic
import types


def build_valid_prefixes():
    prefixes = set()

    stype_for_mtype = {
        types.MT.META: types.ST,
        types.MT.SEMANTIC: types.ST_CC,
        types.MT.CONTENT: types.ST_CC,
        types.MT.DATA: types.ST,
        types.MT.INSTANCE: types.ST,
        types.MT.ISCC: types.ST_ISCC,
        types.MT.ID: types.ST_ID,
    }

    for mtype in types.MT:
        for stype in stype_for_mtype[mtype]:
            digest = ic.write_header(mtype, stype, 0, 0)
            base = ic.encode_base32(digest)
            prefixes.add(base[:2])

    return prefixes


if __name__ == "__main__":
    print(build_valid_prefixes())
