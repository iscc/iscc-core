# -*- coding: utf-8 -*-
"""Build a list of possible base32 encoded ISCC 2-character prefixes for validation"""
import iscc_core as ic


def build_valid_prefixes():
    prefixes = set()

    stype_for_mtype = {
        ic.MT.META: ic.ST,
        ic.MT.SEMANTIC: ic.ST_CC,
        ic.MT.CONTENT: ic.ST_CC,
        ic.MT.DATA: ic.ST,
        ic.MT.INSTANCE: ic.ST,
        ic.MT.ISCC: ic.ST_ISCC,
        ic.MT.ID: ic.ST_ID,
    }

    for mtype in ic.MT:
        for stype in stype_for_mtype[mtype]:
            digest = ic.write_header(mtype, stype, 0, 0)
            base = ic.encode_base32(digest)
            prefixes.add(base[:2])

    return prefixes


if __name__ == "__main__":
    print(build_valid_prefixes())
