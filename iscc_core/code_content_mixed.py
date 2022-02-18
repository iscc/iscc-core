# -*- coding: utf-8 -*-
"""*A similarity hash for mixed media content.*

Creates an ISCC object that provides a `iscc`-field a Mixed-Code and a `parts`-field
that lists the input codes.

Many digital assets embed multiple assets of different mediatypes in a single file.
Text documents may include images, video includes audio in most cases. The ISCC
Content-Code-Mixed encodes the similarity of a collection of assets of the same or
different mediatypes that may occur in a multimedia asset.

Applications that create mixed Content-Codes must be capable to extract embedded
assets and create individual Content-Codes per asset.
"""
from typing import Iterable, Sequence
import iscc_core as ic


__all__ = [
    "gen_mixed_code",
    "gen_mixed_code_v0",
    "soft_hash_codes_v0",
]


def gen_mixed_code(codes, bits=ic.core_opts.mixed_bits):
    # type: (Sequence[str], int) -> dict
    """
    Create an ISCC Content-Code Mixed with the latest standard algorithm.

    :param Iterable[str] codes: a list of Content-Codes.
    :param int bits: Target bit-length of generated Content-Code-Mixed.
    :return: ISCC object with Content-Code Mixed.
    :rtype: dict
    """
    return gen_mixed_code_v0(codes, bits=bits)


def gen_mixed_code_v0(codes, bits=ic.core_opts.mixed_bits):
    # type: (Sequence[str], int) -> dict
    """
    Create an ISCC Content-Code-Mixed with algorithm v0.

    If the provided codes are of mixed length they are stripped to `bits` length for
    calculation.

    :param Iterable[str] codes: a list of Content-Codes.
    :param int bits: Target bit-length of generated Content-Code-Mixed.
    :return: ISCC object with Content-Code Mixed.
    :rtype: dict
    """
    digests = [ic.decode_base32(ic.iscc_clean(code)) for code in codes]
    digest = soft_hash_codes_v0(digests, bits=bits)
    mixed_code = ic.encode_component(
        mtype=ic.MT.CONTENT,
        stype=ic.ST_CC.MIXED,
        version=ic.VS.V0,
        bit_length=bits,
        digest=digest,
    )
    iscc = "ISCC:" + mixed_code
    return dict(iscc=iscc, parts=list(codes))


def soft_hash_codes_v0(cc_digests, bits=ic.core_opts.mixed_bits):
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
    if not len(cc_digests) > 1:
        raise AssertionError("Minimum of 2 codes needed for Content-Code-Mixed.")
    nbytes = bits // 8
    code_tuples = [ic.decode_header(code) for code in cc_digests]
    if not all([ct[0] == ic.MT.CONTENT for ct in code_tuples]):
        raise AssertionError(
            "Only codes with main-type CONTENT allowed as input for Content-Code-Mixed"
        )

    unit_lengths = [ic.decode_length(t[0], t[3]) for t in code_tuples]
    if not all(ul >= bits for ul in unit_lengths):
        raise AssertionError(f"Code to short for {bits}-bit length")

    hash_bytes = []
    # Retain the first byte of the header and strip body to mixed_bits length
    for full, code_tuple in zip(cc_digests, code_tuples):
        hash_bytes.append(full[:1] + code_tuple[-1][: nbytes - 1])
    return ic.alg_simhash(hash_bytes)
