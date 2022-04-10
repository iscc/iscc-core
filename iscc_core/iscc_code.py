# -*- coding: utf-8 -*-
"""*A multi-component identifier for digital media assets.*

An **ISCC-CODE** can be generated from the concatenation of the digests of the following
five **ISCC-UNITs** together with a single common header:

- [Meta-Code](/units/code_meta/) - Encodes metadata similarity
- Semantic-Code - Encodes semantic content similarity (to be developed)
- [Content-Code](/units/content/) - Encodes syntactic/perceptual similarity
- [Data-Code](/units/code_data/) - Encodes raw bitstream similarity
- [Instance-Code](/units/code_instance/) - Data checksum

The following sequences of ISCC-UNITs are possible:

- Data, Instance
- Content, Data, Instance
- Semantic, Data, Instance
- Content, Semantic, Data, Instance
- Meta, Data, Instance
- Meta, Content, Data, Instance
- Meta, Semantic, Data, Instance
- Meta, Semantic, Content, Data, Instance
"""
from typing import Sequence
from operator import itemgetter
import iscc_core as ic


def gen_iscc_code(codes):
    # type: (Sequence[str]) -> dict
    """
    Combine multiple ISCC-UNITs to a composite ISCC-CODE with a common header using
    the latest standard algorithm.

    :param Sequence[str] codes: A valid sequence of singluar ISCC codes.
    :return: An ISCC object with ISCC-CODE
    :rtype: dict
    """
    return gen_iscc_code_v0(codes)


def gen_iscc_code_v0(codes):
    # type: (Sequence[str]) -> dict
    """
    Combine multiple ISCC-UNITS to an ISCC-CODE with a common header using
    algorithm v0.

    :param Sequence[str] codes: A valid sequence of singluar ISCC-UNITS.
    :return: An ISCC object with ISCC-CODE
    :rtype: dict
    """

    codes = [ic.iscc_clean(code) for code in codes]

    # Check basic constraints
    if len(codes) < 2:
        raise ValueError("Minimum two ISCC units required to generate valid ISCC-CODE")
    for code in codes:
        if len(code) < 16:
            raise ValueError(f"Cannot build ISCC-CODE from units shorter than 64-bits: {code}")

    # Decode units and sort by MainType
    decoded = sorted(
        [ic.decode_header(ic.decode_base32(code)) for code in codes], key=itemgetter(0)
    )
    main_types = tuple(d[0] for d in decoded)
    if main_types[-2:] != (ic.MT.DATA, ic.MT.INSTANCE):
        raise ValueError(f"ISCC-CODE requires at least MT.DATA and MT.INSTANCE units.")

    # Determine SubType (generic mediatype)
    sub_types = [t[1] for t in decoded if t[0] in {ic.MT.SEMANTIC, ic.MT.CONTENT}]
    if len(set(sub_types)) > 1:
        raise ValueError(f"Semantic-Code and Content-Code must be of same SubType")
    st = sub_types.pop() if sub_types else ic.ST_ISCC.SUM if len(codes) == 2 else ic.ST_ISCC.NONE

    # Encode unit combination
    encoded_length = ic.encode_units(main_types[:-2])

    # Collect and truncate unit digests to 64-bit
    digest = b"".join([t[-1][:8] for t in decoded])
    header = ic.encode_header(ic.MT.ISCC, st, ic.VS.V0, encoded_length)

    code = ic.encode_base32(header + digest)
    iscc = "ISCC:" + code
    return dict(iscc=iscc)
