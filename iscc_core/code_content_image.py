# -*- coding: utf-8 -*-
"""
*A similarity preserving perceptual hash for images.*

The ISCC Content-Code Image is created by calculating a discrete cosine transform on
normalized image-pixels and comparing the values from the upper left area of the
dct-matrix against their median values to set the hash-bits.
"""
from statistics import median
from typing import Sequence, Tuple
from PIL import Image
from more_itertools import chunked
from iscc_core import codec
from iscc_core.codec import Stream
from iscc_core.schema import ContentCodeImage
from iscc_core.options import opts
from iscc_core.dct import dct


def gen_image_code(img, bits=opts.image_bits):
    # type: (Stream, int) -> ContentCodeImage
    """Create an ISCC Content-Code Image with the latest standard algorithm.

    :param Stream img: Image data stream.
    :param int bits: Bit-length of ISCC Content-Code Image (default 64).
    :return: ISCC Content-Code Image.
    :rtype: ContentCodeImage
    """
    return gen_image_code_v0(img, bits)


def gen_image_code_v0(img, bits=opts.image_bits):
    # type: (Stream, int) -> ContentCodeImage
    """Create an ISCC Content-Code Image with algorithm v0.

    :param Stream img: Image data stream.
    :param int bits: Bit-length of ISCC Content-Code Image (default 64).
    :return: ISCC Content-Code Image.
    :rtype: ContentCodeImage
    """
    pixels, width, height = normalize_image(img)
    digest = soft_hash_image_v0(pixels, bits=bits)
    image_code = codec.encode_component(
        mtype=codec.MT.CONTENT,
        stype=codec.ST_CC.IMAGE,
        version=codec.VS.V0,
        length=bits,
        digest=digest,
    )
    return ContentCodeImage(iscc=image_code, width=width, height=height)


def normalize_image(img):
    # type: (Stream) -> Tuple[Sequence[int], int, int]
    """Normalize image for hash calculation.

    - Add white background to images with alpha transparency
    - Convert to grayscale
    - Resize (bicubic) to 32x32 pixels and flatten

    :param Stream img: Image data stream.
    :return: A tuple of (pixels_1024, original_width, original_height
    :rtype: Tuple[Sequence[int], int, int]
    """

    im = Image.open(img)
    width, height = im.size

    # Add white background to images that have alpha transparency
    if im.mode in ("RGBA", "LA") or (im.mode == "P" and "transparency" in im.info):
        alpha = im.convert("RGBA").split()[-1]
        bg = Image.new("RGBA", im.size, (255, 255, 255, 255))
        bg.paste(im, mask=alpha)
        im = bg

    # Convert to grayscale
    im = im.convert("L")

    # Resize to 32x32
    im = im.resize((32, 32), Image.BICUBIC)

    # A flattened sequence of grayscale pixel values (1024 pixels)
    pixels = im.getdata()

    return pixels, width, height


def soft_hash_image_v0(pixels, bits=opts.image_bits):
    # type: (Sequence[int], int) -> bytes
    """Calculate image hash from normalized grayscale pixel sequence of length 1024.

    :param Sequence[int] pixels:
    :param int bits: Bit-length of image hash (default 64).
    :return: Similarity preserving Image-Hash digest.
    :rtype: bytes
    """

    assert bits <= 256

    # DCT per row
    dct_row_lists = []
    for pixel_list in chunked(pixels, 32):
        dct_row_lists.append(dct(pixel_list))

    # DCT per col
    dct_row_lists_t = list(map(list, zip(*dct_row_lists)))
    dct_col_lists_t = []
    for dct_list in dct_row_lists_t:
        dct_col_lists_t.append(dct(dct_list))

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
