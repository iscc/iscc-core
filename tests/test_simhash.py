# -*- coding: utf-8 -*-
import iscc_core.simhash


def test_similarity_hash():
    all_zero = 0b0.to_bytes(8, "big")
    assert iscc_core.simhash.alg_simhash([all_zero, all_zero]) == all_zero

    all_ones = 0b11111111.to_bytes(1, "big")
    assert iscc_core.simhash.alg_simhash([all_ones, all_ones]) == all_ones

    a = 0b0110.to_bytes(1, "big")
    b = 0b1100.to_bytes(1, "big")
    r = 0b1110.to_bytes(1, "big")
    assert iscc_core.simhash.alg_simhash([a, b]) == r

    a = 0b01101001.to_bytes(1, "big")
    b = 0b00111000.to_bytes(1, "big")
    c = 0b11100100.to_bytes(1, "big")
    r = 0b01101000.to_bytes(1, "big")
    assert iscc_core.simhash.alg_simhash([a, b, c]) == r

    a = 0b01100101.to_bytes(1, "big")
    b = 0b01011001.to_bytes(1, "big")
    c = 0b10010101.to_bytes(1, "big")
    d = 0b10101001.to_bytes(1, "big")
    r = 0b11111101.to_bytes(1, "big")
    assert iscc_core.simhash.alg_simhash([a, b, c, d]) == r

    a = 0b0110100101101001.to_bytes(2, "big")
    b = 0b0011100000111000.to_bytes(2, "big")
    c = 0b1110010011100100.to_bytes(2, "big")
    r = 0b0110100001101000.to_bytes(2, "big")
    assert iscc_core.simhash.alg_simhash([a, b, c]) == r


def test_similarity_hash_256_bit():
    a = bytes.fromhex("84f6a7413bb26202c515fccedfaabfa2f2fc46a69a28a08f7c2a1a12a390ca50")
    b = bytes.fromhex("dc0edccb8e7bff663699f89139af1ff99c276275c4dabd775311bde43c13b34d")
    assert (
        iscc_core.simhash.alg_simhash([a, b]).hex()
        == "dcfeffcbbffbff66f79dfcdfffafbffbfeff66f7defabdff7f3bbff6bf93fb5d"
    )
