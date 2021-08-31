# -*- coding: utf-8 -*-
from typing import List
from iscc_core.base import Stream
from PIL import Image
from more_itertools import chunked


def hash_image(img: Stream) -> bytes:
    return hash_image_v0(img)


def hash_image_v0(img: Stream) -> bytes:
    return


def normalize_image(img: Stream) -> List[List[int]]:
    """Takes image stream and returns a normalized 2D-matrix of greyscale pixels."""

    img = Image.open(img)

    # 1. Add white background to images that have an alpha transparency channel
    if img.mode == "RGBA":
        bg = Image.new("RGB", img.size, (255, 255, 255))
        bg.paste(img, mask=img.split()[3])  # 3 is alpha channel
        img = bg

    # 2. Convert to greyscale
    img = img.convert("L")

    # 3. Resize to 32x32
    img = img.resize((32, 32), Image.BICUBIC)

    # 4. Create 32x32 greyscale pixel matrix
    pixel_matrix = list(chunked(img.getdata(), 32, strict=True))

    return pixel_matrix
