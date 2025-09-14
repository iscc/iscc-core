# -*- coding: utf-8 -*-
import io
import random

import pytest
import iscc_core as ic

wallet = "1Bq568oLhi5HvdgC6rcBSGmu4G3FeAntCz"


def test_gen_iscc_id_v0_single_component():
    tc = ic.gen_text_code_v0("Hello World")
    iscc_id = ic.gen_iscc_id_v0(tc["iscc"], chain_id=0, wallet=wallet)
    assert iscc_id == {"iscc": "ISCC:MAAJU3Y6GCTXLVKA"}
    assert ic.iscc_explain(iscc_id["iscc"]) == "ID-PRIVATE-V0-64-9a6f1e30a775d540"


def test_gen_iscc_id_v0_single_component_uc():
    tc = ic.gen_text_code_v0("Hello World")
    iscc_id = ic.gen_iscc_id_v0(tc["iscc"], chain_id=0, wallet=wallet, uc=1)
    assert iscc_id == {"iscc": "ISCC:MAAZU3Y6GCTXLVKAAE"}
    assert ic.iscc_explain(iscc_id["iscc"]) == "ID-PRIVATE-V0-72-9a6f1e30a775d540-1"


def test_gen_iscc_id_v0_single_component_uc_2byte():
    tc = ic.gen_text_code_v0("Hello World")
    iscc_id = ic.gen_iscc_id_v0(tc["iscc"], 0, wallet=wallet, uc=257)
    assert iscc_id["iscc"] == "ISCC:MABJU3Y6GCTXLVKAQEBA"
    assert ic.iscc_explain(iscc_id["iscc"]) == "ID-PRIVATE-V0-80-9a6f1e30a775d540-257"


def test_gen_iscc_id_v0_multiple_components():
    mc = ic.gen_meta_code_v0("Some Title")["iscc"]
    tc = ic.gen_text_code_v0("Hello World")["iscc"]
    code = ic.iscc_clean(mc) + ic.iscc_clean(tc)
    iscc_id = ic.gen_iscc_id_v0(iscc_code=code, chain_id=1, wallet=wallet)
    assert iscc_id["iscc"] == "ISCC:MEAJU7YOOSTOPYLI"
    assert ic.iscc_explain(iscc_id["iscc"]) == "ID-BITCOIN-V0-64-9a7f0e74a6e7e168"


def test_gen_iscc_id_v0_full_code():
    iscc_code = "ISCC:KQDZJFP6WBM3IIFZ7CRXCNDCNUU3ZEWGL5HAKHNMYHLN2WULPN3ZFHJO7AUS6VQQVM7Q"
    iscc_id = ic.gen_iscc_id_v0(iscc_code=iscc_code, chain_id=1, wallet=wallet)
    assert iscc_id["iscc"] == "ISCC:MEAI5HGE6Z3QHYX7"


def test_gen_iscc_id_v0_instance_only():
    icode = ic.gen_instance_code_v0(io.BytesIO(b"hello world"))
    iscc_id = ic.gen_iscc_id_v0(icode["iscc"], chain_id=0, wallet=wallet)
    assert iscc_id["iscc"] == "ISCC:MAAPVHK2BATN7FK3"
    assert ic.iscc_explain(iscc_id["iscc"]) == "ID-PRIVATE-V0-64-fa9d5a0826df955b"


def test_gen_iscc_id_v0_data_instance():
    icode = ic.gen_instance_code_v0(io.BytesIO(b"hello world"))
    dc = ic.gen_data_code_v0(io.BytesIO(b"hello world"))
    iscc_sum = ic.gen_iscc_code_v0([icode["iscc"], dc["iscc"]])
    iscc_id = ic.gen_iscc_id_v0(iscc_sum["iscc"], chain_id=0, wallet=wallet)
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
    with pytest.raises(ValueError):
        ic.iscc_id_incr_v0(mc)


def test_incr_iscc_id_v0_raises_wrong_vs():
    mc = ic.Code.rnd(ic.MT.ID)
    head = list(mc._head)
    head[2] = 1
    mc._head = tuple(head)
    with pytest.raises(ValueError):
        ic.iscc_id_incr_v0(mc.code)


def test_gen_iscc_id_v0_raises_chain_id():
    code = ic.Code.rnd(ic.MT.ISCC, bits=256)
    with pytest.raises(ValueError):
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
    with pytest.raises(ValueError):
        ic.iscc_id_incr_v0(iscc_id)


def test_iscc_id_incr_wrong_maintype():
    # Test with META MainType instead of ID
    meta_code = ic.encode_component(ic.MT.META, ic.ST.NONE, 0, 64, b"\x00" * 8)
    with pytest.raises(ValueError, match="MainType .* is not ISCC-ID"):
        ic.iscc_id_incr(meta_code)


def test_iscc_id_incr_unsupported_version():
    # Create an ID with an unsupported version (e.g., version 2)
    # We need to manually construct this as normal functions won't create version 2
    header = ic.encode_header(ic.MT.ID, ic.ST_ID.PRIVATE, 2, 64)  # Version 2
    digest = b"\x00" * 8
    code_bytes = header + digest
    iscc_code = ic.encode_base32(code_bytes)
    with pytest.raises(ValueError, match="Unsupported ISCC-ID version"):
        ic.iscc_id_incr(iscc_code)


def test_iscc_id_unit_types():
    # Meta-Code 256-bits only
    mc = ic.Code.rnd(mt=ic.MT.META, bits=256)
    assert ic.gen_iscc_id_v0(mc.code, 0, "a") == {"iscc": "ISCC:MAAMUFVSHK6CYVQW"}
    assert ic.gen_iscc_id_v0(mc.uri, 0, "a") == {"iscc": "ISCC:MAAMUFVSHK6CYVQW"}

    # Meta-Code 64-bit prefix
    mc2 = ic.encode_component(ic.MT.META, ic.ST.NONE, 0, bit_length=64, digest=mc.hash_bytes[:8])
    assert ic.gen_iscc_id_v0(mc2, 0, "a") == {"iscc": "ISCC:MAAMUFVSHK6CYVQW"}

    cc = ic.Code.rnd(mt=ic.MT.CONTENT, bits=64)
    assert ic.gen_iscc_id_v0(cc.code, 0, "a") == {"iscc": "ISCC:MAAOXNCHOPSVHG2M"}

    fc = ic.Code.rnd(mt=ic.MT.FLAKE, bits=64)
    assert ic.gen_iscc_id_v0(fc.code, 0, "a") == {"iscc": "ISCC:MAALUWZEW5VYL4FE"}


def test_iscc_id_from_iscc_id_raises():
    iid = ic.Code.rnd(mt=ic.MT.ID, bits=64)
    assert iid.code == "MIAORZJBNL6L2BGD"
    with pytest.raises(ValueError):
        ic.gen_iscc_id_v0(iid.code, 0, "a")
