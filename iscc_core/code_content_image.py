# -*- coding: utf-8 -*-
"""
*A similarity preserving perceptual hash for images.*

The ISCC Content-Code Image is created by calculating a discrete cosine transform on
normalized image-pixels and comparing the values from the upper left area of the
dct-matrix against their median values to set the hash-bits.
"""
from statistics import median
from typing import Sequence, Tuple
from PIL import Image, ImageChops, ImageOps
from more_itertools import chunked
from iscc_core import codec
from iscc_core.codec import Stream
from iscc_core.schema import ContentCodeImage
from iscc_core.options import opts
from iscc_core.dct import dct
from loguru import logger as log


def gen_image_code(pixels, bits=opts.image_bits):
    # type: (Sequence[int], int) -> ContentCodeImage
    """Create an ISCC Content-Code Image with the latest standard algorithm.

    :param Sequence[int] pixels: Normalized image pixels (32x32 flattened gray values).
    :param int bits: Bit-length of ISCC Content-Code Image (default 64).
    :return: ISCC Content-Code Image.
    :rtype: ContentCodeImage
    """
    return gen_image_code_v0(pixels, bits)


def gen_image_code_v0(pixels, bits=opts.image_bits):
    # type: (Sequence[int], int) -> ContentCodeImage
    """Create an ISCC Content-Code Image with algorithm v0.

    :param Sequence[int] pixels: Normalized image pixels (32x32 flattened gray values)
    :param int bits: Bit-length of ISCC Content-Code Image (default 64).
    :return: ISCC Content-Code Image.
    :rtype: ContentCodeImage
    """
    digest = soft_hash_image_v0(pixels, bits=bits)
    image_code = codec.encode_component(
        mtype=codec.MT.CONTENT,
        stype=codec.ST_CC.IMAGE,
        version=codec.VS.V0,
        length=bits,
        digest=digest,
    )
    return ContentCodeImage(iscc=image_code)


def normalize_image(img):
    # type: (Stream) -> Tuple[Sequence[int], int, int]
    """Normalize image for hash calculation.

    :param Stream img: Image data stream.
    :return: A tuple of (pixels_1024, original_width, original_height
    :rtype: Tuple[Sequence[int], int, int]
    """

    im = Image.open(img)

    # Transpose image according to EXIF Orientation tag
    if opts.image_transpose:
        im = transpose_image(im)

    # Add gray background to image if it has alpha transparency
    if opts.image_fill:
        im = fill_image(im)

    # Trim uniform colored (empty) border if there is one
    if opts.image_trim:
        im = trim_image(im)

    # Convert to grayscale
    im = im.convert("L")

    # Resize to 32x32
    im = im.resize((32, 32), Image.BICUBIC)

    # A flattened sequence of grayscale pixel values (1024 pixels)
    pixels = im.getdata()

    return pixels


def transpose_image(imo):
    # type: (Image.Image) -> Image.Image
    """
    Transpose image according to EXIF Orientation tag

    :param Image imo: PIL.Image object
    :return: EXIF transposed image
    :rtype: Image.Image
    """
    imo = ImageOps.exif_transpose(imo)
    log.debug(f"Image exif transpose applied")
    return imo


def fill_image(imo):
    # type: (Image.Image) -> Image.Image
    """
    Add gray background to image if it has alpha transparency

    :param Image imo: PIL.Image object
    :return: Image where alpha transparency is replaced with gray background.
    :rtype: Image.Image
    """
    if imo.mode in ("RGBA", "LA") or (imo.mode == "P" and "transparency" in imo.info):
        if imo.mode != "RGBA":
            imo = imo.convert("RGBA")
        bg = Image.new("RGBA", imo.size, (126, 126, 126))
        imo = Image.alpha_composite(bg, imo)
        log.debug(f"Image transparency filled with gray")
    return imo


def trim_image(imo):
    # type: (Image.Image) -> Image.Image
    """Trim uniform colored (empty) border.

    Takes the upper left pixel as reference to

    :param Image.Image imo: PIL.Image object
    :return: Image with uniform colored (empty) border removed.
    :rtype: Image.Image
    """

    bg = Image.new(imo.mode, imo.size, imo.getpixel((0, 0)))
    diff = ImageChops.difference(imo, bg)
    diff = ImageChops.add(diff, diff)
    bbox = diff.getbbox()
    if bbox:
        log.debug(f"Image has been trimmed")
        return imo.crop(bbox)
    return imo


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
