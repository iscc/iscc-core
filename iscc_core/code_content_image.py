# -*- coding: utf-8 -*-
"""
A similarity preserving perceptual hash for image content.
"""
import math
from statistics import median
from typing import Sequence
from PIL import Image
from more_itertools import chunked
from iscc_core import codec
from iscc_core.base import Stream


def gen_image_code(img, bits=64):
    # type: (Stream, int) -> str
    """Create an ISCC Content-Code Image with the latest standard algorithm.

    :param Stream img: Image data stream.
    :param int bits: Bit-length of ISCC Content-Code Image (default 64).
    :retun: ISCC Content-Code Image.
    :rtype: str
    """
    return gen_image_code_v0(img, bits)


def gen_image_code_v0(img, bits=64):
    # type: (Stream, int) -> str
    """Create an ISCC Content-Code Image with algorithm v0.

    :param Stream img: Image data stream.
    :param int bits: Bit-length of ISCC Content-Code Image (default 64).
    :retun: ISCC Content-Code Image.
    :rtype: str
    """
    pixels = normalize_image(img)
    digest = hash_image_v0(pixels, bits=bits)
    image_code = codec.encode_component(
        mtype=codec.MT.CONTENT,
        stype=codec.ST_CC.IMAGE,
        version=codec.VS.V0,
        length=bits,
        digest=digest,
    )
    return image_code


def normalize_image(img):
    # type: (Stream) -> Sequence[int]
    """Create a normalized sequence of pixels from an Image.

    :param Stream img: Image data stream.
    :return: A sequence of 1024 normalized image pixels
    :rtype: Sequence[int]
    """

    im = Image.open(img)

    # Add white background to images that have alpha transparency
    if im.mode in ("RGBA", "LA") or (im.mode == "P" and "transparency" in im.info):
        alpha = im.convert("RGBA").split()[-1]
        bg = Image.new("RGBA", im.size, (255, 255, 255, 255))
        bg.paste(im, mask=alpha)
        im = bg

    # Convert to greyscale
    im = im.convert("L")

    # Resize to 32x32
    im = im.resize((32, 32), Image.BICUBIC)

    # A flattened sequence of grayscale pixel values (1024 pixels)
    pixels = im.getdata()

    return pixels


def hash_image_v0(pixels: Sequence[int], bits=64) -> bytes:
    """Calculate image hash from normalized grayscale pixel sequence of length 1024.

    :param Sequence[int] pixels:
    :param int bits: Bit-length of image hash (default 64)
    :return: similarity preserving byte hash
    :rtype: bytes
    """

    # DCT per row
    dct_row_lists = []
    for pixel_list in chunked(pixels, 32):
        dct_row_lists.append(dct(pixel_list))

    # DCT per col
    dct_row_lists_t = list(map(list, zip(*dct_row_lists)))
    dct_col_lists_t = []
    for dct_list in dct_row_lists_t:
        dct_col_lists_t.append(dct(dct_list))

    dct_lists = list(map(list, zip(*dct_col_lists_t)))

    # Extract upper left 8 x 8 corner
    flat_list = [x for sublist in dct_lists[:8] for x in sublist[:8]]

    # Calculate median
    med = median(flat_list)

    # Create 64-bit digest by comparing to median
    bitstring = ""
    for value in flat_list:
        if value > med:
            bitstring += "1"
        else:
            bitstring += "0"

    if bits in (32, 64):
        hash_digest = int(bitstring, 2).to_bytes(8, "big", signed=False)
    else:
        # Extend to 256-bit
        flat_list_ext = [x for sublist in dct_lists[8:22] for x in sublist[8:22]]
        med = median(flat_list_ext)
        for value in flat_list_ext[:192]:
            if value > med:
                bitstring += "1"
            else:
                bitstring += "0"
        hash_digest = int(bitstring, 2).to_bytes(32, "big", signed=False)

    return hash_digest


def dct(v: Sequence[float]):
    """
    Discrete cosine transform by Project Nayuki. (MIT License)
    See: https://www.nayuki.io/page/fast-discrete-cosine-transform-algorithms
    """

    n = len(v)
    if n == 1:
        return list(v)
    elif n == 0 or n % 2 != 0:
        raise ValueError()
    else:
        half = n // 2
        alpha = [(v[i] + v[-(i + 1)]) for i in range(half)]
        beta = [
            (v[i] - v[-(i + 1)]) / (math.cos((i + 0.5) * math.pi / n) * 2.0)
            for i in range(half)
        ]
        alpha = dct(alpha)
        beta = dct(beta)
        result = []
        for i in range(half - 1):
            result.append(alpha[i])
            result.append(beta[i] + beta[i + 1])
        result.append(alpha[-1])
        result.append(beta[-1])
        return result
