# -*- coding: utf-8 -*-
"""*A similarity hash for mixed media content.*

Creates an ISCC object that provides a `iscc`-field a Mixed-Code and a `parts`-field
that lists the input codes.

Many digital assets embed multiple assets of different mediatypes in a single file.
Text documents may including images, video includes audio in most cases. The ISCC
Content-Code-Mixed encodes the similarity of a collection of assets of the same or
different mediatypes that may occur in a multi-media asset.

Applications that create mixed Content-Codes must be capable to extract embedded
assets and create individual Content-Codes per asset.
"""
from typing import Iterable, Sequence

import iscc_core
from iscc_core import codec, core_opts
from iscc_core.schema import ISCC
from iscc_core.simhash import similarity_hash


def gen_mixed_code(codes, bits=core_opts.mixed_bits):
    # type: (Sequence[str], int) -> ISCC
    """
    Create an ISCC Content-Code Mixed with the latest standard algorithm.

    :param Iterable[str] codes: a list of Content-Codes.
    :param int bits: Target bit-length of generated Content-Code-Mixed.
    :return: ISCC object with Content-Code Mixed.
    :rtype: ISCC
    """
    return gen_mixed_code_v0(codes, bits=bits)


def gen_mixed_code_v0(codes, bits=core_opts.mixed_bits):
    # type: (Sequence[str], int) -> ISCC
    """
    Create an ISCC Content-Code-Mixed with algorithm v0.

    If the provided codes are of mixed length they are stripped to `bits` length for
    calculation.

    :param Iterable[str] codes: a list of Content-Codes.
    :param int bits: Target bit-length of generated Content-Code-Mixed.
    :return: ISCC object with Content-Code Mixed.
    :rtype: ISCC
    """
    digests = [codec.decode_base32(iscc_core.clean(code)) for code in codes]
    digest = soft_hash_codes_v0(digests, bits=bits)
    mixed_code = codec.encode_component(
        mtype=codec.MT.CONTENT,
        stype=codec.ST_CC.MIXED,
        version=codec.VS.V0,
        bit_length=bits,
        digest=digest,
    )
    iscc = "ISCC:" + mixed_code
    return ISCC(iscc=iscc, parts=codes)


def soft_hash_codes_v0(cc_digests, bits=core_opts.mixed_bits):
    # type: (Sequence[bytes], int) -> bytes
    """
    Create a similarity hash from multiple Content-Code digests.

    The similarity hash is created from the bodies of the input codes with the first
    byte of the code-header prepended.

    All codes must be of main-type CONTENT and have a minimum length of `bits`.

    :param Sequence[bytes] cc_digests: a list of Content-Code digests.
    :param int bits: Target bit-length of generated Content-Code-Mixed.
    :return: Similarity preserving byte hash.
    :rtype: bytes
    """
    assert len(cc_digests) > 1, "Minimum of 2 codes needed for Content-Code-Mixed."
    nbytes = bits // 8
    code_tuples = [codec.read_header(code) for code in cc_digests]
    assert all(
        [ct[0] == codec.MT.CONTENT for ct in code_tuples]
    ), "Only codes with main-type CONTENT allowed as input for Content-Code-Mixed"

    unit_lengths = [codec.decode_length(t[0], t[3]) for t in code_tuples]
    assert all(
        ul >= bits for ul in unit_lengths
    ), "Code to short for {}-bit length".format(bits)

    hash_bytes = []
    # Retain the first byte of the header and strip body to mixed_bits length
    for full, code_tuple in zip(cc_digests, code_tuples):
        hash_bytes.append(full[:1] + code_tuple[-1][: nbytes - 1])
    return similarity_hash(hash_bytes)
