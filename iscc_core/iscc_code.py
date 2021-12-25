# -*- coding: utf-8 -*-
"""*A multi-component identifier for digital media assets.*

An **ISCC-CODE** is generated from the concatenation of the digests of the following
four components together with a single common header:

- [Meta-Code](/components/code_meta/) - Encodes metadata similarity
- [Content-Code](/components/content/) - Encodes syntactic/perceptual similarity
- [Data-Code](/components/code_data/) - Encodes raw bitstream similarity
- [Instance-Code](/components/code_instance/) - Data checksum

The following combinations of components are possible:

- Meta, Content, Data, Instance (256-bit / 64-bit per component)
- Content, Data, Instance (192-bit / 64-bit per component)
- Data, Instance (256 or 128 bit / 64 or 128-bit per component)
"""
from operator import itemgetter
from typing import Iterable
from iscc_core.schema import ISCC
import iscc_core as ic


def gen_iscc_code(codes):
    # type: (Iterable[str]) -> ISCC
    """
    Combine multiple ISCC components to a composite ISCC-CODE with a common header using
    the latest standard algorithm.

    :param Iterable[str] codes: A valid sequence of singluar ISCC codes.
    :return: An ISCC object with ISCC-CODE
    :rtype: ISCC
    """
    return gen_iscc_code_v0(codes)


def gen_iscc_code_v0(codes):
    # type: (Iterable[str]) -> ISCC
    """
    Combine multiple ISCC components to a composite ISCC-CODE with a common header using
    algorithm v0.

    :param Iterable[str] codes: A valid sequence of singluar ISCC codes.
    :return: An ISCC object with ISCC-CODE
    :rtype: ISCC
    """

    # Validate combinatorial constraints
    valid_mt_mix = {
        (ic.MT.META, ic.MT.CONTENT, ic.MT.DATA, ic.MT.INSTANCE),
        (ic.MT.CONTENT, ic.MT.DATA, ic.MT.INSTANCE),
        (ic.MT.DATA, ic.MT.INSTANCE),
    }

    # TODO: add suport for Semantic-Code

    decoded = sorted(
        [ic.read_header(ic.decode_base32(code)) for code in codes], key=itemgetter(0)
    )
    main_types = tuple(d[0] for d in decoded)

    assert main_types in valid_mt_mix, f"Combinatorial constraint error: {main_types}"

    # Validate component length contraints
    lengths = set(d[3] for d in decoded)
    assert all(l >= 64 for l in lengths), f"Component length constraint error {lengths}"

    # Validate component version constraints
    versions = set(d[2] for d in decoded)
    assert all(v == ic.VS.V0 for v in versions), f"Version constraint error {versions}"

    # Derive per component length
    is_di = main_types == (ic.MT.DATA, ic.MT.INSTANCE)
    long_codes = all(d[3] >= 128 for d in decoded)
    if is_di and long_codes:
        component_nbytes = 128 // 8
    else:
        component_nbytes = 64 // 8

    # Concatenate bodies
    body = b"".join([d[-1][:component_nbytes] for d in decoded])

    # Construct header values
    mt = ic.MT.ISCC
    st = ic.ST_ISCC.SUM
    for d in decoded:
        if d[0] == ic.MT.CONTENT:
            st = d[1]
            break
    ln = (component_nbytes * len(decoded)) * 8

    # Build ISCC
    iscc_code = ic.encode_component(mt, st, ic.VS.V0, ln, body)

    return ISCC(iscc=iscc_code)
