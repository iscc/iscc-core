# -*- coding: utf-8 -*-
import io
import os
import random

import pytest
import iscc_core as ic

A_INT = 0b00000000_00001111_00000000_00000000_00000000_00000000_00000000_00000000
B_INT = 0b11110000_00001111_00000000_00000000_00000000_00000000_00000000_00000000
A_BYT = A_INT.to_bytes(length=8, byteorder="big", signed=False)
B_BYT = B_INT.to_bytes(length=8, byteorder="big", signed=False)


def test_hamming_distance():
    assert ic.iscc_distance_bytes(A_BYT, B_BYT) == 4


def test_similarity_single_64():
    ia = ic.Code.rnd(mt=ic.MT.CONTENT, st=ic.ST_ISCC.IMAGE, bits=64, data=A_BYT).code
    ib = ic.Code.rnd(mt=ic.MT.CONTENT, st=ic.ST_ISCC.IMAGE, bits=64, data=B_BYT).code
    assert ic.iscc_similarity(ia, ib) == 93


def test_similarity_single_256():
    a = "AAD7SATLZUS57KXZZL2HXAD7HT6264AHEIRZQ4QTLB6LHVRXNTLE7MA"
    b = "AAD7CATK5QX46LX5YL2HXIH7FT626UAHE4RYC4QTDB6LXVRXNDJE7MA"
    assert ic.iscc_similarity(a, b) == 90


def test_similarity_composite():
    a = "KQD7SATLZUS57KXZN2N6SA6A3THBJRQW4B5CZPGWU2PR566ZQNLM2AA"
    b = "KQD7CATK5QX46LX5N2N6SA6A3THBJRQW4B5CZPGWU2PR566ZQNLM2AA"
    assert ic.iscc_similarity(a, b) == 96


def test_distance_single_64():
    ia = ic.Code.rnd(mt=ic.MT.CONTENT, st=ic.ST_ISCC.IMAGE, bits=64, data=A_BYT).code
    ib = ic.Code.rnd(mt=ic.MT.CONTENT, st=ic.ST_ISCC.IMAGE, bits=64, data=B_BYT).code
    assert ic.iscc_distance(ia, ib) == 4


def test_distance_single_256():
    a = "AAD7SATLZUS57KXZZL2HXAD7HT6264AHEIRZQ4QTLB6LHVRXNTLE7MA"
    b = "AAD7CATK5QX46LX5YL2HXIH7FT626UAHE4RYC4QTDB6LXVRXNDJE7MA"
    assert ic.iscc_distance(a, b) == 24


def test_distance_composite():
    a = "KQD7SATLZUS57KXZN2N6SA6A3THBJRQW4B5CZPGWU2PR566ZQNLM2AA"
    b = "KQD7CATK5QX46LX5N2N6SA6A3THBJRQW4B5CZPGWU2PR566ZQNLM2AA"
    assert ic.iscc_distance(a, b) == 10


def test_sliding_window():
    assert list(ic.utils.sliding_window("", width=4)) == [""]
    assert list(ic.utils.sliding_window("A", width=4)) == ["A"]
    assert list(ic.utils.sliding_window("Hello", width=4)) == ["Hell", "ello"]
    words = ("lorem", "ipsum", "dolor", "sit", "amet")
    slices = list(ic.utils.sliding_window(words, 2))
    assert slices[0] == ("lorem", "ipsum")
    assert slices[1] == ("ipsum", "dolor")
    assert slices[-1] == ("sit", "amet")


def test_sliding_window_retains_sequence_type():
    tuple_sequence = ("lorem", "ipsum", "dolor", "sit", "amet")
    slices = list(ic.utils.sliding_window(tuple_sequence, 2))
    assert isinstance(slices[0], tuple)

    list_sequence = list(tuple_sequence)
    slices = list(ic.utils.sliding_window(list_sequence, 2))
    assert isinstance(slices[0], list)

    text_sequence = "lorem"
    slices = list(ic.utils.sliding_window(text_sequence, 2))
    assert isinstance(slices[0], str)
    assert slices[0] == "lo"
    assert slices[1] == "or"
    assert slices[-1] == "em"


def test_sliding_window_bigger_than_sequence():
    words = ("lorem", "ipsum", "dolor", "sit", "amet")
    slices = list(ic.utils.sliding_window(words, 6))
    assert slices[0] == words

    slices = list(ic.utils.sliding_window("hello", 5))
    assert slices[0] == "hello"


def test__safe_unpack():
    a = ic.Code.rnd(ic.MT.META, bits=64).code
    b = ic.Code.rnd(ic.MT.DATA, bits=64).code
    with pytest.raises(ValueError):
        ic.utils.iscc_pair_unpack(a, b)


def test_cidv1_hex_stream():
    assert (
        ic.cidv1_hex(io.BytesIO(b"hello world"))
        == "f01551220b94d27b9934d3e08a52e52d7da7dabfac484efe37a5380ee9088f7ace2efcde9"
    )


def test_cidv1_hex_bytes():
    assert (
        ic.cidv1_hex(b"hello world")
        == "f01551220b94d27b9934d3e08a52e52d7da7dabfac484efe37a5380ee9088f7ace2efcde9"
    )


def test_hash_ipfs_cidv1_max(static_bytes):
    data = static_bytes[:262144]
    assert (
        ic.cidv1_hex(io.BytesIO(data))
        == "f01551220dd8186a3d57826d3179717fbcaef8e4c24c5380f0ee7d869f41f727015fe17ab"
    )


def test_cidv1_to_token_id():
    token_id = ic.cidv1_to_token_id(
        "f01551220dd8186a3d57826d3179717fbcaef8e4c24c5380f0ee7d869f41f727015fe17ab"
    )
    assert token_id <= 2**256 - 1
    assert (
        token_id == 100189992059221005740937582782800178391670948768450295424002582041064650971051
    )


def test_cidv1_to_token_id_raises():
    with pytest.raises(ValueError):
        ic.cidv1_to_token_id("bafkrei...")
    with pytest.raises(ValueError):
        ic.cidv1_to_token_id(
            "f02551220b94d27b9934d3e08a52e52d7da7dabfac484efe37a5380ee9088f7ace2efcde9"
        )
    with pytest.raises(ValueError):
        ic.cidv1_to_token_id(
            "f01551220b94d27b9934d3e08a52e52d7da7dabfac484efe37a5380ee9088f7ace2efcd"
        )


def test_cidv1_from_token_id():
    cidv1 = ic.cidv1_from_token_id(
        100189992059221005740937582782800178391670948768450295424002582041064650971051
    )
    assert cidv1 == "f01551220dd8186a3d57826d3179717fbcaef8e4c24c5380f0ee7d869f41f727015fe17ab"


def test_hash_ipfs_cidv1_raises(static_bytes):
    data = static_bytes[:262145]
    with pytest.raises(ValueError):
        ic.cidv1_hex(io.BytesIO(data))


def test_canonicalize():
    value = {"hello": "world"}
    assert ic.json_canonical(value) == b'{"hello":"world"}'


def test_canonicalize_non_ascii():
    value = {"hello": "wörld"}
    assert ic.json_canonical(value) == b'{"hello":"w\xc3\xb6rld"}'


def test_canonicalize_small_int():
    value = {"num": 2**52}
    assert ic.json_canonical(value) == b'{"num":4503599627370496}'


def test_canonicalize_large_int():
    value = {"num": 2**53}
    assert ic.json_canonical(value) == b'{"num":9007199254740992}'
    with pytest.raises(ValueError):
        value = {"num": 2**53 + 1}
        ic.json_canonical(value)


def test_sliding_window_raises():
    with pytest.raises(AssertionError):
        ic.sliding_window([1, 2, 3, 4, 5], 1)


def test_hamming_distance_raises():
    a, b = os.urandom(8), os.urandom(9)
    with pytest.raises(AssertionError):
        ic.iscc_distance_bytes(a, b)


def test_multi_hash_blake3():
    assert (
        ic.multi_hash_blake3(b"")
        == "1e20af1349b9f5f9a1a6a0404dea36dcc9499bcb25c9adc112b7cc9a93cae41f3262"
    )
    assert (
        ic.multi_hash_blake3(b"hello world")
        == "1e20d74981efa70a0c880b8d8c1985d075dbcbf679b99a5f9914e5aaf96b831a9e24"
    )


def test_iscc_compare():
    # reset randomness
    ic.Code.rgen = random.Random(0)
    a = ic.Code.rnd(mt=ic.MT.ISCC, bits=256)
    assert ic.iscc_compare(a.code, a.code) == {
        "meta_dist": 0,
        "semantic_dist": 0,
        "data_dist": 0,
        "instance_match": True,
    }

    b = ic.Code.rnd(mt=ic.MT.ISCC, bits=256)
    assert ic.iscc_compare(a.code, b.code) == {
        "meta_dist": 22,
        "semantic_dist": 34,
        "data_dist": 30,
        "instance_match": False,
    }


def test_wide_subtype_similarity():
    """Test similarity calculation for ISCC codes with WIDE subtype."""
    # Two identical WIDE ISCCs (128-bit Data + 128-bit Instance)
    a = "K4AP5Q74YXNZC4EKRCQEKOXKMYHCJV2JQHX2OCQMRAFY3DAZQXIHLWY"
    b = "K4AP5Q74YXNZC4EKRCQEKOXKMYHCJV2JQHX2OCQMRAFY3DAZQXIHLWY"
    assert ic.iscc_similarity(a, b) == 100

    # WIDE ISCCs with some differences in both Data and Instance parts
    c = "K4AP5Q74YXNZC4EKRCQEKOXKMYHCJV2JQHX2OCQMRAFY3DAZQXIHLWY"
    d = "K4AJVXNYPUVJYVGZOOX2V6MOWVBJEG4ET747CO7OEXGK5ZHMFAUXLCI"
    # Should detect the differences
    sim = ic.iscc_similarity(c, d)
    assert 50 <= sim < 100


def test_wide_subtype_compare():
    """Test component-wise comparison for ISCC codes with WIDE subtype."""
    # Create WIDE ISCCs that should decompose into two 128-bit components
    a = "K4AP5Q74YXNZC4EKRCQEKOXKMYHCJV2JQHX2OCQMRAFY3DAZQXIHLWY"
    b = "K4AP5Q74YXNZC4EKRCQEKOXKMYHCJV2JQHX2OCQMRAFY3DAZQXIHLWY"

    # Same codes should have zero distance and instance match
    result = ic.iscc_compare(a, b)
    assert "data_dist" in result
    assert "instance_match" in result
    assert result["data_dist"] == 0
    assert result["instance_match"] is True

    # Different WIDE ISCCs
    c = "K4AP5Q74YXNZC4EKRCQEKOXKMYHCJV2JQHX2OCQMRAFY3DAZQXIHLWY"
    d = "K4AJVXNYPUVJYVGZOOX2V6MOWVBJEG4ET747CO7OEXGK5ZHMFAUXLCI"

    # Should correctly detect differences in components
    result = ic.iscc_compare(c, d)
    assert "data_dist" in result
    assert "instance_match" in result
    assert result["data_dist"] > 0
    assert result["instance_match"] is False


def test_similarity_iscc_idv1():
    """Test that similarity comparison raises for ISCC-IDv1."""
    # Generate two different ISCC-IDv1s
    id1 = ic.gen_iscc_id_v1(1234567890, 42)["iscc"]
    id2 = ic.gen_iscc_id_v1(1234567891, 42)["iscc"]

    # Create a regular ISCC code for testing
    regular_code = ic.Code.rnd(mt=ic.MT.CONTENT, st=ic.ST_CC.TEXT, bits=64).code

    # Test both branches - IDv1 as first arg and as second arg
    with pytest.raises(ValueError, match="Similarity comparison not supported for ISCC-IDv1"):
        ic.iscc_similarity(id1, regular_code)  # IDv1 as first arg

    with pytest.raises(ValueError, match="Similarity comparison not supported for ISCC-IDv1"):
        ic.iscc_similarity(regular_code, id1)  # IDv1 as second arg

    with pytest.raises(ValueError, match="Similarity comparison not supported for ISCC-IDv1"):
        ic.iscc_distance(id1, regular_code)

    # Compare should return simple match result
    result = ic.iscc_compare(id1, id2)
    assert "id_match" in result
    assert isinstance(result["id_match"], bool)

    # Same IDs should match
    result = ic.iscc_compare(id1, id1)
    assert result["id_match"] is True


def test_iscc_nph_distance_equal_length():
    """Test Normalized Prefix Hamming Distance with equal length byte strings."""
    # Test with identical byte strings
    a = b"hello world"
    b = b"hello world"
    result = ic.utils.iscc_nph_distance_bytes(a, b)
    assert result["distance"] == 0.0
    assert result["common_prefix_bits"] == len(a) * 8

    # Test with different byte strings of equal length
    a = b"hello world"
    b = b"jello world"  # One character different
    result = ic.utils.iscc_nph_distance_bytes(a, b)
    # 'h' (0x68) vs 'j' (0x6A) has 2 bits different
    assert 0.0 < result["distance"] < 1.0
    assert result["common_prefix_bits"] == len(a) * 8

    # Test with completely different byte strings
    a = b"hello world"
    b = b"HELLO WORLD"  # All characters different in case
    result = ic.utils.iscc_nph_distance_bytes(a, b)
    assert 0.0 < result["distance"] < 1.0
    assert result["common_prefix_bits"] == len(a) * 8


def test_iscc_nph_distance_different_length():
    """Test Normalized Prefix Hamming Distance with different length byte strings."""
    # Test with one string longer than the other
    a = b"hello world"
    b = b"hello"
    result = ic.utils.iscc_nph_distance_bytes(a, b)
    assert result["distance"] == 0.0  # Common prefix is identical
    assert result["common_prefix_bits"] == len(b) * 8

    # Test with one string longer and different content
    a = b"hello world"
    b = b"jello"
    result = ic.utils.iscc_nph_distance_bytes(a, b)
    # 'h' (0x68) vs 'j' (0x6A) has 2 bits different
    assert 0.0 < result["distance"] < 1.0
    assert result["common_prefix_bits"] == len(b) * 8


def test_iscc_nph_distance_empty():
    """Test Normalized Prefix Hamming Distance with empty byte strings."""
    # Both strings empty
    a = b""
    b = b""
    result = ic.utils.iscc_nph_distance_bytes(a, b)
    assert result["distance"] == 0.0
    assert result["common_prefix_bits"] == 0

    # One string empty
    a = b"hello world"
    b = b""
    result = ic.utils.iscc_nph_distance_bytes(a, b)
    assert result["distance"] == 1.0
    assert result["common_prefix_bits"] == 0

    # Other string empty
    a = b""
    b = b"hello world"
    result = ic.utils.iscc_nph_distance_bytes(a, b)
    assert result["distance"] == 1.0
    assert result["common_prefix_bits"] == 0


def test_iscc_nph_similarity_equal_length():
    """Test Normalized Prefix Hamming Similarity with equal length byte strings."""
    # Test with identical byte strings
    a = b"hello world"
    b = b"hello world"
    result = ic.utils.iscc_nph_similarity_bytes(a, b)
    assert result["similarity"] == 1.0
    assert result["common_prefix_bits"] == len(a) * 8

    # Test with different byte strings of equal length
    a = b"hello world"
    b = b"jello world"  # One character different
    result = ic.utils.iscc_nph_similarity_bytes(a, b)
    # 'h' (0x68) vs 'j' (0x6A) has 2 bits different
    assert 0.0 < result["similarity"] < 1.0
    assert result["common_prefix_bits"] == len(a) * 8

    # Test with completely different byte strings
    a = b"hello world"
    b = b"HELLO WORLD"  # All characters different in case
    result = ic.utils.iscc_nph_similarity_bytes(a, b)
    assert 0.0 < result["similarity"] < 1.0
    assert result["common_prefix_bits"] == len(a) * 8


def test_iscc_nph_similarity_different_length():
    """Test Normalized Prefix Hamming Similarity with different length byte strings."""
    # Test with one string longer than the other
    a = b"hello world"
    b = b"hello"
    result = ic.utils.iscc_nph_similarity_bytes(a, b)
    assert result["similarity"] == 1.0  # Common prefix is identical
    assert result["common_prefix_bits"] == len(b) * 8

    # Test with one string longer and different content
    a = b"hello world"
    b = b"jello"
    result = ic.utils.iscc_nph_similarity_bytes(a, b)
    # 'h' (0x68) vs 'j' (0x6A) has 2 bits different
    assert 0.0 < result["similarity"] < 1.0
    assert result["common_prefix_bits"] == len(b) * 8


def test_iscc_nph_similarity_empty():
    """Test Normalized Prefix Hamming Similarity with empty byte strings."""
    # Both strings empty
    a = b""
    b = b""
    result = ic.utils.iscc_nph_similarity_bytes(a, b)
    assert result["similarity"] == 1.0
    assert result["common_prefix_bits"] == 0

    # One string empty
    a = b"hello world"
    b = b""
    result = ic.utils.iscc_nph_similarity_bytes(a, b)
    assert result["similarity"] == 0.0
    assert result["common_prefix_bits"] == 0

    # Other string empty
    a = b""
    b = b"hello world"
    result = ic.utils.iscc_nph_similarity_bytes(a, b)
    assert result["similarity"] == 0.0
    assert result["common_prefix_bits"] == 0


def test_iscc_nph_compare_identical_units():
    """Test NPH comparison of identical ISCC units."""
    # Create identical content codes
    code = ic.Code.rnd(mt=ic.MT.CONTENT, st=ic.ST_CC.TEXT, bits=64)
    result = ic.iscc_nph_compare(code.code, code.code)

    assert "CONTENT_TEXT_V0" in result
    assert result["CONTENT_TEXT_V0"]["similarity"] == 1.0
    assert result["CONTENT_TEXT_V0"]["common_prefix_bits"] == 64


def test_iscc_nph_compare_different_units():
    """Test NPH comparison of different ISCC units of same type."""
    ic.Code.rgen = random.Random(0)
    code_a = ic.Code.rnd(mt=ic.MT.CONTENT, st=ic.ST_CC.TEXT, bits=64)
    code_b = ic.Code.rnd(mt=ic.MT.CONTENT, st=ic.ST_CC.TEXT, bits=64)

    result = ic.iscc_nph_compare(code_a.code, code_b.code)

    assert "CONTENT_TEXT_V0" in result
    assert 0.0 <= result["CONTENT_TEXT_V0"]["similarity"] <= 1.0
    assert result["CONTENT_TEXT_V0"]["common_prefix_bits"] == 64


def test_iscc_nph_compare_different_lengths():
    """Test NPH comparison handles different length components."""
    # Create codes with different bit lengths
    code_64 = ic.Code.rnd(mt=ic.MT.CONTENT, st=ic.ST_CC.TEXT, bits=64)
    code_128 = ic.Code.rnd(mt=ic.MT.CONTENT, st=ic.ST_CC.TEXT, bits=128)

    result = ic.iscc_nph_compare(code_64.code, code_128.code)

    assert "CONTENT_TEXT_V0" in result
    # Should compare common prefix (64 bits)
    assert result["CONTENT_TEXT_V0"]["common_prefix_bits"] == 64


def test_iscc_nph_compare_iscc_code():
    """Test NPH comparison of ISCC-CODEs."""
    ic.Code.rgen = random.Random(0)
    code_a = ic.Code.rnd(mt=ic.MT.ISCC, bits=256)
    code_b = ic.Code.rnd(mt=ic.MT.ISCC, bits=256)

    result = ic.iscc_nph_compare(code_a.code, code_b.code)

    # Should have results for meta, semantic, data, and instance components
    # The exact keys depend on the subtypes, but we can check the structure
    assert len(result) >= 4  # At least 4 components

    # All results should have similarity and common_prefix_bits
    for key, value in result.items():
        assert "similarity" in value
        assert "common_prefix_bits" in value
        assert 0.0 <= value["similarity"] <= 1.0
        # Keys should be in format MAINTYPE_SUBTYPE_VERSION
        assert key.count("_") == 2


def test_iscc_nph_compare_mixed_unit_and_code():
    """Test NPH comparison between ISCC-UNIT and ISCC-CODE."""
    ic.Code.rgen = random.Random(0)
    content_unit = ic.Code.rnd(mt=ic.MT.CONTENT, st=ic.ST_CC.TEXT, bits=64)
    iscc_code = ic.Code.rnd(mt=ic.MT.ISCC, bits=256)

    # The ISCC-CODE should contain a semantic component that might match
    result = ic.iscc_nph_compare(content_unit.code, iscc_code.code)

    # Should compare the matching semantic component if present
    # Result depends on the random generation
    assert isinstance(result, dict)


def test_iscc_nph_compare_non_matching_types():
    """Test NPH comparison with non-matching component types."""
    ic.Code.rgen = random.Random(0)
    meta_code = ic.Code.rnd(mt=ic.MT.META, bits=64)
    content_code = ic.Code.rnd(mt=ic.MT.CONTENT, st=ic.ST_CC.TEXT, bits=64)

    result = ic.iscc_nph_compare(meta_code.code, content_code.code)

    # No matching components, should return empty dict
    assert result == {}


def test_iscc_nph_compare_instance_component():
    """Test NPH comparison with INSTANCE components."""
    ic.Code.rgen = random.Random(0)
    code_a = ic.Code.rnd(mt=ic.MT.ISCC, bits=256)
    code_b = ic.Code.rnd(mt=ic.MT.ISCC, bits=256)

    result = ic.iscc_nph_compare(code_a.code, code_b.code)

    # Should have an INSTANCE component with binary similarity (0.0 or 1.0)
    instance_keys = [k for k in result.keys() if k.startswith("INSTANCE_")]
    assert len(instance_keys) == 1

    instance_key = instance_keys[0]
    assert "similarity" in result[instance_key]
    assert "common_prefix_bits" in result[instance_key]
    # INSTANCE similarity should be binary
    assert result[instance_key]["similarity"] in [0.0, 1.0]


def test_iscc_nph_compare_skips_iscc_id():
    """Test NPH comparison skips ISCC-ID components."""
    # Create an ISCC-IDv1
    iscc_id = ic.gen_iscc_id_v1(1234567890, 42)["iscc"]

    # Create a regular content code
    content_code = ic.Code.rnd(mt=ic.MT.CONTENT, st=ic.ST_CC.TEXT, bits=64).code

    # Compare ISCC-ID with content code - ID should be skipped
    result = ic.iscc_nph_compare(iscc_id, content_code)

    # Result should be empty since ID components are skipped and there's no match
    assert result == {}
