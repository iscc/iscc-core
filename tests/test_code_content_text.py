# -*- coding: utf-8 -*-
from iscc_core import code_content_text

TEXT_A = u"""
    Their most significant and usefull property of similarity-preserving
    fingerprints gets lost in the fragmentation of individual, propietary and
    use case specific implementations. The real benefit lies in similarity
    preservation beyond your local data archive on a global scale accross
    vendors.
"""

TEXT_B = u"""
    The most significant and usefull property of similarity-preserving
    fingerprints gets lost in the fragmentation of individual, propietary and
    use case specific implementations. The real benefit lies in similarity
    preservation beyond your local data archive on a global scale accross
    vendors.
"""

TEXT_C = u"""
    A need for open standard fingerprinting. We don´t need the best
    Fingerprinting algorithm just an accessible and widely used one.
"""


def test_hash_text_a():
    a = code_content_text.hash_text_v0(TEXT_A).hex()
    assert a == "1f869a735c10bf9c32107ab4114e13d2bf93614cda99513ee9f989faf3d6983f"


def test_hash_text_b():
    b = code_content_text.hash_text_v0(TEXT_B).hex()
    assert b == "1f869a735c18bfcc32107ab4114e13d2bf9b614cda91513ee9f189faf3d6987f"


def test_hash_text_c():
    c = code_content_text.hash_text_v0(TEXT_C).hex()
    assert c == "366f2f1b08ba65efbbb48acf4b9953d144be674fa0af8802e7a6f1769b19c576"


def test_code_text_a_default():
    a = code_content_text.code_text_v0(TEXT_A)
    assert a == "EAAR7BU2ONOBBP44"


def test_code_text_b_128_bits():
    b = code_content_text.code_text_v0(TEXT_B, 128)
    assert b == "EABR7BU2ONOBRP6MGIIHVNARJYJ5E"


def test_code_text_c_256_bits():
    c = code_content_text.code_text_v0(TEXT_C, 256)
    assert c == "EADTM3ZPDMELUZPPXO2IVT2LTFJ5CRF6M5H2BL4IALT2N4LWTMM4K5Q"
