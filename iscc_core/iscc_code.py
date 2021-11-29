# -*- coding: utf-8 -*-
"""*The canonical multi-component identifier for digital media assets.*

An **ISCC-CODE** is generated from the concatenation of the digests of the following
four components together with a single common header:

- [Meta-Code][iscc_core.code_meta] - Encodes metadata similarity
- [Content-Code](/components/content/) - Encodes syntactic/perceptual similarity
- [Data-Code][iscc_core.code_data] - Encodes raw bitstream similarity
- [Instance-Code][iscc_core.code_instance] - Data checksum
"""
from operator import attrgetter
from typing import Iterable

from iscc_core import Code
from iscc_core.codec import AnyISCC, LN, MT, VS


def gen_iscc_code(codes):
    # type: (Iterable[AnyISCC]) -> Code
    """
    Combine ISCC components to an ISCC-CODE with a single common header using the latest
    standard algorithm.

    :param Iterable[AnyISCC] codes: A sequence of Meta, Content, Data, Instance codes.
    :return: Code object of full ISCC-CODE
    :rtype: Code
    """
    return gen_iscc_code_v01(codes)


def gen_iscc_code_v01(codes):
    # type: (Iterable[AnyISCC]) -> Code
    """
    Combine ISCC components to an ISCC-CODE with a single common header using
    algorithm v0.

    :param Iterable[AnyISCC] codes: A sequence of Meta, Content, Data, Instance codes.
    :return: Code object of full ISCC-CODE
    :rtype: Code
    """
    codes = sorted([Code(c) for c in codes], key=attrgetter("maintype"))
    assert len(codes) == 4, "ISCC composition requires 4 codes"
    assert all(c.version == VS.V0 for c in codes), "Codes must all be v0"

    types = tuple(c.maintype for c in codes)
    assert MT.ID not in types, "Cannot compose ISCC-ID"
    assert MT.ISCC not in types, "Cannot compose canonical ISCC code"

    assert types == (
        MT.META,
        MT.CONTENT,
        MT.DATA,
        MT.INSTANCE,
    ), "Codes must be META, CONTENT, DATA, INSTANCE"

    for code in codes:
        assert code.length >= LN.L64, "ISCC requires min 64-bit codes"
        chash = b""
        for c in codes:
            chash += c.hash_bytes[:8]
    return Code((MT.ISCC, codes[1].subtype, codes[1].version, LN.L256, chash))
