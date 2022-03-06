# -*- coding: utf-8 -*-
"""*A similarity preserving perceptual hash for images.*

The ISCC Content-Code Image is created by calculating a discrete cosine transform on
normalized image-pixels and comparing the values from the upper left area of the
dct-matrix against their median values to set the hash-bits.

Images must be normalized before using gen_image_code. Prepare images as follows:

- Transpose image according to EXIF Orientation
- Add white background to image if it has alpha transparency
- Crop empty borders of image
- Convert image to grayscale
- Resize image to 32x32
- Flatten 32x32 matrix to an array of 1024 grayscale (uint8) pixel values
"""
from statistics import median
from typing import Sequence
from more_itertools import chunked
import iscc_core as ic


__all__ = [
    "gen_image_code",
    "gen_image_code_v0",
    "soft_hash_image_v0",
]


def gen_image_code(pixels, bits=ic.core_opts.image_bits):
    # type: (Sequence[int], int) -> dict
    """
    Create an ISCC Content-Code Image with the latest standard algorithm.

    :param Sequence[int] pixels: Normalized image pixels (32x32 flattened gray values).
    :param int bits: Bit-length of ISCC Content-Code Image (default 64).
    :return: ISCC object with Content-Code Image.
    :rtype: ISCC
    """
    return gen_image_code_v0(pixels, bits)


def gen_image_code_v0(pixels, bits=ic.core_opts.image_bits):
    # type: (Sequence[int], int) -> dict
    """
    Create an ISCC Content-Code Image with algorithm v0.

    :param Sequence[int] pixels: Normalized image pixels (32x32 flattened gray values)
    :param int bits: Bit-length of ISCC Content-Code Image (default 64).
    :return: ISCC object with Content-Code Image.
    :rtype: ISCC
    """
    digest = soft_hash_image_v0(pixels, bits=bits)
    image_code = ic.encode_component(
        mtype=ic.MT.CONTENT,
        stype=ic.ST_CC.IMAGE,
        version=ic.VS.V0,
        bit_length=bits,
        digest=digest,
    )
    iscc = "ISCC:" + image_code
    return {"iscc": iscc}


def soft_hash_image_v0(pixels, bits=ic.core_opts.image_bits):
    # type: (Sequence[int], int) -> bytes
    """
    Calculate image hash from normalized grayscale pixel sequence of length 1024.

    :param Sequence[int] pixels:
    :param int bits: Bit-length of image hash (default 64).
    :return: Similarity preserving Image-Hash digest.
    :rtype: bytes
    """
    if not bits <= 256:
        raise AssertionError(f"{bits} bits exeeds max lenght 256 for soft_hash_image")

    # DCT per row
    dct_row_lists = []
    for pixel_list in chunked(pixels, 32):
        dct_row_lists.append(ic.alg_dct(pixel_list))

    # DCT per col
    dct_row_lists_t = list(map(list, zip(*dct_row_lists)))
    dct_col_lists_t = []
    for dct_list in dct_row_lists_t:
        dct_col_lists_t.append(ic.alg_dct(dct_list))

    dct_matrix = list(map(list, zip(*dct_col_lists_t)))

    def flatten(m, x, y):
        """Extract and flatten an 8 x 8 slice from a 2d matrix starting at col/row."""
        return [v for sublist in m[y : y + 8] for v in sublist[x : x + 8]]

    bitstring = ""
    slices = ((0, 0), (1, 0), (0, 1), (1, 1))

    for xy in slices:
        # Extract 8 x 8 slice
        flat_list = flatten(dct_matrix, *xy)

        # Calculate median
        med = median(flat_list)

        # Append 64-bit digest by comparing to median
        for value in flat_list:
            if value > med:
                bitstring += "1"
            else:
                bitstring += "0"
        bl = len(bitstring)
        if bl >= bits:
            hash_digest = int(bitstring, 2).to_bytes(bl // 8, "big", signed=False)
            return hash_digest
