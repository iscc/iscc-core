# -*- coding: utf-8 -*-
from statistics import median
from typing import List
from iscc_core.dct import dct


def hash_image(pixels: List[List[int]]) -> bytes:
    """Calculate image hash from 64x64 grayscale pixel matrix."""
    return hash_image_v0(pixels)


def hash_image_v0(pixels: List[List[int]]) -> bytes:
    """Calculate image hash from 64*64 grayscale pixel matrix."""

    # 1. DCT per row
    dct_row_lists = []
    for pixel_list in pixels:
        dct_row_lists.append(dct(pixel_list))

    # 2. DCT per col
    dct_row_lists_t = list(map(list, zip(*dct_row_lists)))
    dct_col_lists_t = []
    for dct_list in dct_row_lists_t:
        dct_col_lists_t.append(dct(dct_list))

    dct_lists = list(map(list, zip(*dct_col_lists_t)))

    # 3. Extract upper left 16x16 corner
    flat_list = [x for sublist in dct_lists[:16] for x in sublist[:16]]

    # 4. Calculate median
    med = median(flat_list)

    # 5. Create 64-bit digest by comparing to median
    bitstring = ""
    for value in flat_list:
        if value > med:
            bitstring += "1"
        else:
            bitstring += "0"
    hash_digest = int(bitstring, 2).to_bytes(32, "big", signed=False)

    return hash_digest
