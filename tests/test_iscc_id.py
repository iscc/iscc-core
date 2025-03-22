# -*- coding: utf-8 -*-
import io
import random

import pytest
import iscc_core as ic

wallet = "1Bq568oLhi5HvdgC6rcBSGmu4G3FeAntCz"


def test_gen_iscc_id_v0_single_component():
    tc = ic.gen_text_code_v0("Hello World")
    iscc_id = ic.gen_iscc_id(tc["iscc"], chain_id=0, wallet=wallet)
    assert iscc_id == {"iscc": "ISCC:MAAJU3Y6GCTXLVKA"}
    assert ic.iscc_explain(iscc_id["iscc"]) == "ID-PRIVATE-V0-64-9a6f1e30a775d540"


def test_gen_iscc_id_v0_single_component_uc():
    tc = ic.gen_text_code_v0("Hello World")
    iscc_id = ic.gen_iscc_id(tc["iscc"], chain_id=0, wallet=wallet, uc=1)
    assert iscc_id == {"iscc": "ISCC:MAAZU3Y6GCTXLVKAAE"}
    assert ic.iscc_explain(iscc_id["iscc"]) == "ID-PRIVATE-V0-72-9a6f1e30a775d540-1"


def test_gen_iscc_id_v0_single_component_uc_2byte():
    tc = ic.gen_text_code_v0("Hello World")
    iscc_id = ic.gen_iscc_id(tc["iscc"], 0, wallet=wallet, uc=257)
    assert iscc_id["iscc"] == "ISCC:MABJU3Y6GCTXLVKAQEBA"
    assert ic.iscc_explain(iscc_id["iscc"]) == "ID-PRIVATE-V0-80-9a6f1e30a775d540-257"


def test_gen_iscc_id_v0_multiple_components():
    mc = ic.gen_meta_code_v0("Some Title")["iscc"]
    tc = ic.gen_text_code_v0("Hello World")["iscc"]
    code = ic.iscc_clean(mc) + ic.iscc_clean(tc)
    iscc_id = ic.gen_iscc_id(iscc_code=code, chain_id=1, wallet=wallet)
    assert iscc_id["iscc"] == "ISCC:MEAJU7YOOSTOPYLI"
    assert ic.iscc_explain(iscc_id["iscc"]) == "ID-BITCOIN-V0-64-9a7f0e74a6e7e168"


def test_gen_iscc_id_v0_full_code():
    iscc_code = "ISCC:KQDZJFP6WBM3IIFZ7CRXCNDCNUU3ZEWGL5HAKHNMYHLN2WULPN3ZFHJO7AUS6VQQVM7Q"
    iscc_id = ic.gen_iscc_id(iscc_code=iscc_code, chain_id=1, wallet=wallet)
    assert iscc_id["iscc"] == "ISCC:MEAI5HGE6Z3QHYX7"


def test_gen_iscc_id_v0_instance_only():
    icode = ic.gen_instance_code_v0(io.BytesIO(b"hello world"))
    iscc_id = ic.gen_iscc_id(icode["iscc"], chain_id=0, wallet=wallet)
    assert iscc_id["iscc"] == "ISCC:MAAPVHK2BATN7FK3"
    assert ic.iscc_explain(iscc_id["iscc"]) == "ID-PRIVATE-V0-64-fa9d5a0826df955b"


def test_gen_iscc_id_v0_data_instance():
    icode = ic.gen_instance_code_v0(io.BytesIO(b"hello world"))
    dc = ic.gen_data_code_v0(io.BytesIO(b"hello world"))
    iscc_sum = ic.gen_iscc_code_v0([icode["iscc"], dc["iscc"]])
    iscc_id = ic.gen_iscc_id(iscc_sum["iscc"], chain_id=0, wallet=wallet)
    assert iscc_id["iscc"] == "ISCC:MAAIVNGQOUGKGDRH"
    assert ic.iscc_explain(iscc_id["iscc"]) == "ID-PRIVATE-V0-64-8ab4d0750ca30e27"


def test_incr_iscc_id():
    assert ic.iscc_id.iscc_id_incr("ISCC:MAADB7WD7TC5XELQ") == "MAATB7WD7TC5XELQAE"


def test_incr_iscc_id_no_prefix_explain():
    incr = ic.iscc_id.iscc_id_incr("MAADB7WD7TC5XELQ")
    assert ic.Code(incr).explain == "ID-PRIVATE-V0-72-30fec3fcc5db9170-1"


def test_incr_iscc_id_v0():
    assert ic.Code("ISCC:MAADB7WD7TC5XELQ").explain == "ID-PRIVATE-V0-64-30fec3fcc5db9170"
    assert ic.iscc_id.iscc_id_incr_v0("ISCC:MAADB7WD7TC5XELQ") == "MAATB7WD7TC5XELQAE"
    assert ic.Code("ISCC:MAATB7WD7TC5XELQAE").explain == "ID-PRIVATE-V0-72-30fec3fcc5db9170-1"

    assert ic.iscc_id.iscc_id_incr_v0("ISCC:MAATB7WD7TC5XELQAE") == "MAATB7WD7TC5XELQAI"
    assert ic.Code("MAATB7WD7TC5XELQAI").explain == "ID-PRIVATE-V0-72-30fec3fcc5db9170-2"


def test_incr_iscc_id_v0_raises_wrong_mt():
    mc = ic.Code.rnd(ic.MT.META).code
    with pytest.raises(AssertionError):
        ic.iscc_id_incr_v0(mc)


def test_incr_iscc_id_v0_raises_wrong_vs():
    mc = ic.Code.rnd(ic.MT.ID)
    head = list(mc._head)
    head[2] = 1
    mc._head = tuple(head)
    with pytest.raises(AssertionError):
        ic.iscc_id_incr_v0(mc.code)


def test_gen_iscc_id_v0_raises_chain_id():
    code = ic.Code.rnd(ic.MT.ISCC, bits=256)
    with pytest.raises(AssertionError):
        ic.gen_iscc_id_v0(code.code, 5, wallet=wallet)


def test_alg_simhash_from_iscc_id():
    shash = ic.alg_simhash_from_iscc_id("MAAJU3Y6GCTXLVKA", wallet=wallet)
    assert shash == "20250db96e0d4a17"


def test_iscc_id_incr_v0_vs_uc():
    # reset randomness
    ic.Code.rgen = random.Random(0)

    iscc_code = ic.Code.rnd(ic.MT.ISCC, bits=256)
    assert (
        iscc_code.explain
        == "ISCC-VIDEO-V0-MSDI-c8a70639eb1167b367a9c3787c65c1e582e2e662f728b4fa42485e3a0a5d2f34"
    )
    iscc_id_a = ic.gen_iscc_id_v0(iscc_code.code, ic.ST_ID.POLYGON, "testwallet", uc=0).get("iscc")
    assert iscc_id_a == "ISCC:MMAMJ2RTNK6TRZGB"
    assert ic.Code(iscc_id_a).explain == "ID-POLYGON-V0-64-c4ea336abd38e4c1"

    # incremennt via uc
    iscc_id_b = ic.gen_iscc_id_v0(iscc_code.code, ic.ST_ID.POLYGON, "testwallet", uc=1).get("iscc")
    assert iscc_id_b == "ISCC:MMA4J2RTNK6TRZGBAE"
    assert ic.Code(iscc_id_b).explain == "ID-POLYGON-V0-72-c4ea336abd38e4c1-1"

    # plain increment
    iscc_id_c = ic.iscc_id_incr_v0(iscc_id_a)
    assert iscc_id_c == "MMA4J2RTNK6TRZGBAE"
    assert ic.Code(iscc_id_c).explain == "ID-POLYGON-V0-72-c4ea336abd38e4c1-1"

    # both increments are identical
    assert iscc_id_b == "ISCC:" + iscc_id_c


def test_iscc_id_incr_v0_raises_bad_chain_id():
    iscc_id = ic.encode_component(ic.MT.ID, 4, 0, 64, b"\x00" * 8)
    assert iscc_id == "MQAAAAAAAAAAAAAA"
    with pytest.raises(AssertionError):
        ic.iscc_id_incr_v0(iscc_id)


def test_iscc_id_unit_types():
    # Meta-Code 256-bits only
    mc = ic.Code.rnd(mt=ic.MT.META, bits=256)
    assert ic.gen_iscc_id(mc.code, 0, "a") == {"iscc": "ISCC:MAAMUFVSHK6CYVQW"}
    assert ic.gen_iscc_id(mc.uri, 0, "a") == {"iscc": "ISCC:MAAMUFVSHK6CYVQW"}

    # Meta-Code 64-bit prefix
    mc2 = ic.encode_component(ic.MT.META, ic.ST.NONE, 0, bit_length=64, digest=mc.hash_bytes[:8])
    assert ic.gen_iscc_id(mc2, 0, "a") == {"iscc": "ISCC:MAAMUFVSHK6CYVQW"}

    cc = ic.Code.rnd(mt=ic.MT.CONTENT, bits=64)
    assert ic.gen_iscc_id(cc.code, 0, "a") == {"iscc": "ISCC:MAAOXNCHOPSVHG2M"}

    fc = ic.Code.rnd(mt=ic.MT.FLAKE, bits=64)
    assert ic.gen_iscc_id(fc.code, 0, "a") == {"iscc": "ISCC:MAALUWZEW5VYL4FE"}


def test_iscc_id_from_iscc_id_raises():
    iid = ic.Code.rnd(mt=ic.MT.ID, bits=64)
    assert iid.code == "MIAORZJBNL6L2BGD"
    with pytest.raises(ValueError):
        ic.gen_iscc_id(iid.code, 0, "a")


def test_gen_iscc_id_v1_basic():
    """Test basic functionality of gen_iscc_id_v1."""
    # Use a fixed timestamp and server_id for deterministic testing
    timestamp = 1714503123456789  # Some timestamp in microseconds
    server_id = 42  # Server ID between 0-4095

    iscc_id = ic.gen_iscc_id_v1(timestamp=timestamp, server_id=server_id)
    assert iscc_id == {"iscc": "ISCC:MAIGC5KN3I6TCUBK"}
    assert ic.iscc_explain(iscc_id["iscc"]) == "ID-REALM_0-V1-64-18c4f5f5c6f5c02a"


def test_gen_iscc_id_v1_timestamp_overflow():
    """Test that timestamp overflow raises ValueError."""
    # Create a timestamp that exceeds 52 bits
    overflow_timestamp = 2**52
    server_id = 1

    with pytest.raises(ValueError, match="Timestamp overflow"):
        ic.gen_iscc_id_v1(timestamp=overflow_timestamp, server_id=server_id)


def test_gen_iscc_id_v1_server_id_range():
    """Test with different server IDs within valid range."""
    timestamp = 1714503123456789

    # Test with minimum server_id (0)
    min_id = ic.gen_iscc_id_v1(timestamp=timestamp, server_id=0)
    assert min_id == {"iscc": "ISCC:MAIGC5KN3I6TCUAA"}

    # Test with maximum server_id (4095)
    max_id = ic.gen_iscc_id_v1(timestamp=timestamp, server_id=4095)
    assert max_id == {"iscc": "ISCC:MAIGC5KN3I6TCX77"}


def test_gen_iscc_id_v1_different_realms():
    """Test with different realm IDs."""
    timestamp = 1714503123456789
    server_id = 42

    # Test with realm_id = 1
    realm1 = ic.gen_iscc_id_v1(timestamp=timestamp, server_id=server_id, realm_id=1)
    assert realm1 == {"iscc": "ISCC:MEIGC5KN3I6TCUBK"}
    assert ic.iscc_explain(realm1["iscc"]) == "ID-REALM_1-V1-64-18c4f5f5c6f5c02a"

    # Test with realm_id = 15 (maximum valid realm_id)
    realm15 = ic.gen_iscc_id_v1(timestamp=timestamp, server_id=server_id, realm_id=15)
    assert realm15 == {"iscc": "ISCC:MIYEXNVXNBXVGAAK"}
    assert ic.iscc_explain(realm15["iscc"]) == "ID-REALM_15-V1-64-18c4f5f5c6f5c02a"


def test_gen_iscc_id_v1_structure():
    """Test the internal structure of the ISCC-ID v1."""
    timestamp = 1000000000000000  # Easy to recognize timestamp
    server_id = 123  # Easy to recognize server_id

    iscc_id = ic.gen_iscc_id_v1(timestamp=timestamp, server_id=server_id)

    # Decode the ISCC-ID to verify its structure
    code = ic.Code(iscc_id["iscc"])

    # Check header components
    assert code.maintype == ic.MT.ID
    assert code.subtype == 0  # Default realm_id
    assert code.version == ic.VS.V1
    assert code.length == 64  # 64-bit length

    # Check that the digest contains our timestamp and server_id
    # The digest is 8 bytes (64 bits) where:
    # - First 52 bits (6.5 bytes) are the timestamp
    # - Last 12 bits (1.5 bytes) are the server_id
    digest_int = int.from_bytes(code.hash_bytes, byteorder="big")

    # Extract server_id (last 12 bits)
    extracted_server_id = digest_int & 0xFFF  # 0xFFF = 12 bits of 1s
    assert extracted_server_id == server_id

    # Extract timestamp (first 52 bits)
    extracted_timestamp = digest_int >> 12
    assert extracted_timestamp == timestamp
