# -*- coding: utf-8 -*-
"""*ISCC - a multi-component identifier for digital media assets.*

An **ISCC-CODE** is generated from the concatenation of the digests of the following
four components together with a single common header:

- [Meta-Code][iscc_core.code_meta] - Encodes metadata similarity
- [Content-Code](/components/content/) - Encodes syntactic/perceptual similarity
- [Data-Code][iscc_core.code_data] - Encodes raw bitstream similarity
- [Instance-Code][iscc_core.code_instance] - Data checksum

The following combinations of components are possible:

- Meta, Content, Data, Instance (256-bit / 64-bit per component)
- Content, Data, Instance (192-bit / 64-bit per component)
- Data, Instance (256 or 128 bit / 64 or 128-bit per component)
"""
from operator import itemgetter
from typing import Iterable
from iscc_core import codec as co
from iscc_core.schema import IsccCode


def gen_iscc_code(codes):
    # type: (Iterable[str]) -> IsccCode
    """
    Combine multiple ISCC components to a composite ISCC with a common header using
    the latest standard algorithm.

    :param Iterable[str] codes: A valid sequence of singluar ISCC codes.
    :return: An IsccCode object
    :rtype: IsccCode
    """
    return gen_iscc_code_v0(codes)


def gen_iscc_code_v0(codes):
    # type: (Iterable[str]) -> IsccCode
    """
    Combine multiple ISCC components to a composite ISCC with a common header using
    algorithm v0.

    :param Iterable[str] codes: A valid sequence of singluar ISCC codes.
    :return: An IsccCode object
    :rtype: IsccCode
    """

    # Validate combinatorial constraints
    valid_mt_mix = {
        (co.MT.META, co.MT.CONTENT, co.MT.DATA, co.MT.INSTANCE),
        (co.MT.CONTENT, co.MT.DATA, co.MT.INSTANCE),
        (co.MT.DATA, co.MT.INSTANCE),
    }

    # TODO: add suport for Semantic-Code

    decoded = sorted(
        [co.read_header(co.decode_base32(code)) for code in codes], key=itemgetter(0)
    )
    main_types = tuple(d[0] for d in decoded)

    assert main_types in valid_mt_mix, f"Combinatorial constraint error: {main_types}"

    # Validate component length contraints
    lengths = set(d[3] for d in decoded)
    assert all(l >= 64 for l in lengths), f"Component length constraint error {lengths}"

    # Validate component version constraints
    versions = set(d[2] for d in decoded)
    assert all(v == co.VS.V0 for v in versions), f"Version constraint error {versions}"

    # Derive per component length
    is_di = main_types == (co.MT.DATA, co.MT.INSTANCE)
    long_codes = all(d[3] >= 128 for d in decoded)
    if is_di and long_codes:
        component_nbytes = 128 // 8
    else:
        component_nbytes = 64 // 8

    # Concatenate bodies
    body = b"".join([d[-1][:component_nbytes] for d in decoded])

    # Construct header values
    mt = co.MT.ISCC
    st = co.ST_CC.NONE
    for d in decoded:
        if d[0] == co.MT.CONTENT:
            st = d[1]
            break
    ln = (component_nbytes * len(decoded)) * 8

    # Build ISCC
    iscc_code = co.encode_component(mt, st, co.VS.V0, ln, body)

    return IsccCode(iscc=iscc_code)
