# -*- coding: utf-8 -*-
import iscc_core


def test_ISCC_json():
    mc = iscc_core.gen_meta_code("Hello", "World")
    assert (
        mc.json() == '{"@context": "https://purl.org/iscc/context/0.2.0.json", '
        '"type": "https://purl.org/iscc/schema/0.2.0.json", '
        '"iscc": "ISCC:AAAWKLHFXNSF7NNE", "name": "hello", "description": "world", '
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
        b'"description":"world","iscc":"ISCC:AAAWKLHFXNSF7NNE",'
        b'"metahash":"bf73d18575a736e4037d45f9e316085b86c19be6363de6aa789e13deaacc1c4e",'
        b'"name":"hello","type":"https://purl.org/iscc/schema/0.2.0.json"}'
    )


def test_ISCC_ipfs_hash():
    mc = iscc_core.gen_meta_code("Hello", "World")
    assert mc.ipfs_hash() == "f0155171c8244be3d0c3fdef42c69e0362f67c118631546178d22bc488c8f32cc"


def test_ISCC_jsonld_context():
    assert "@context" in iscc_core.ISCC.jsonld_context()


# def test_ISCC_jsonld_norm():
#     mc = iscc_core.gen_meta_code("Hello", "World")
#     assert mc.jsonld_norm().startswith("<ISCC:AAAWKLHFXNSF7NNE>")
