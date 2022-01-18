# -*- coding: utf-8 -*-
import iscc_core


def test_ISCC_json():
    mc = iscc_core.gen_meta_code("Hello", "World")
    assert mc.json() == (
        '{"@context": "https://purl.org/iscc/context/0.2.0.json", "type": '
        '"https://purl.org/iscc/schema/0.2.0.json", "iscc": "ISCC:AAAWKLHFXNSF7NNE", '
        '"name": "Hello", "description": "World", "metahash": '
        '"bdyqed6bziei6w4j2eilfyrwjbk4pb7mtthesakh5nuuisrfsh72365q"}'
    )


def test_ISCC_code():
    mc = iscc_core.gen_meta_code("Hello", "World")
    assert mc.code == "AAAWKLHFXNSF7NNE"


def test_ISCC_jcs():
    mc = iscc_core.gen_meta_code("Hello", "World")
    assert mc.jcs() == (
        b'{"@context":"https://purl.org/iscc/context/0.2.0.json","description":"World"'
        b',"iscc":"ISCC:AAAWKLHFXNSF7NNE","metahash":"bdyqed6bziei6w4j2eilfyrwjbk4pb7m'
        b'tthesakh5nuuisrfsh72365q","name":"Hello","type":"https://purl.org/iscc/schem'
        b'a/0.2.0.json"}'
    )


def test_ISCC_ipfs_hash():
    mc = iscc_core.gen_meta_code("Hello", "World")
    assert mc.ipfs_hash() == "f0155171c923a412f3c3350c325ea2cd8ca73e3dc459e7552ddecb6f4c59a97d8"


def test_ISCC_jsonld_context():
    assert "@context" in iscc_core.ISCC.jsonld_context()


# def test_ISCC_jsonld_norm():
#     mc = iscc_core.gen_meta_code("Hello", "World")
#     assert mc.jsonld_norm().startswith("<ISCC:AAAWKLHFXNSF7NNE>")
