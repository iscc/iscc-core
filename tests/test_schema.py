# -*- coding: utf-8 -*-
import iscc_core


def test_ISCC_json():
    mc = iscc_core.gen_meta_code("Hello", "World")
    assert (
        mc.json() == '{"@context": "https://purl.org/iscc/context/0.2.0.json", '
        '"type": "https://purl.org/iscc/schema/0.2.0.json", '
        '"iscc": "AAAWKLHFXNSF7NNE", "name": "Hello", "description": "World", '
        '"metahash": '
        '"bf73d18575a736e4037d45f9e316085b86c19be6363de6aa789e13deaacc1c4e"}'
    )


def test_ISCC_code():
    mc = iscc_core.gen_meta_code("Hello", "World")
    assert mc.code == "AAAWKLHFXNSF7NNE"


def test_ISCC_jcs():
    mc = iscc_core.gen_meta_code("Hello", "World")
    assert mc.jcs() == (
        b'{"@context":"https://purl.org/iscc/context/0.2.0.json",'
        b'"description":"World","iscc":"AAAWKLHFXNSF7NNE",'
        b'"metahash":"bf73d18575a736e4037d45f9e316085b86c19be6363de6aa789e13deaacc1c4e",'
        b'"name":"Hello","type":"https://purl.org/iscc/schema/0.2.0.json"}'
    )


def test_ISCC_ipfs_hash():
    mc = iscc_core.gen_meta_code("Hello", "World")
    assert (
        mc.ipfs_hash()
        == "f0155171c90e8a3fad4b881d51acabda09d39fd65d90a35360ff1d53a6d391103"
    )


def test_ISCC_jsonld_context():
    assert "@context" in iscc_core.ISCC.jsonld_context()


def test_ISCC_jsonld_norm():
    mc = iscc_core.gen_meta_code("Hello", "World")
    assert mc.jsonld_norm().startswith("<ISCC:AAAWKLHFXNSF7NNE>")
