from io import BytesIO

from iscc_schema import ISCC

import iscc_core


def test_hash_instance_v0_empty():
    digest = iscc_core.code_instance.hash_instance_v0(BytesIO(b""))
    assert digest.hex() == "af1349b9f5f9a1a6a0404dea36dcc9499bcb25c9adc112b7cc9a93cae41f3262"


def test_hash_instance_v0_zero():
    digest = iscc_core.code_instance.hash_instance_v0(BytesIO(b"\x00"))
    assert digest.hex() == "2d3adedff11b61f14c886e35afa036736dcd87a74d27b5c1510225d0f592e213"


def test_gen_instance_code_v0_empty_default():
    ic_obj = iscc_core.code_instance.gen_instance_code_v0(BytesIO(b""))
    assert ic_obj == dict(
        iscc="ISCC:IAA26E2JXH27TING",
        datahash="bdyqk6e2jxh27tingubae32rw3teutg6lexe23qisw7gjve6k4qpteyq",
        filesize=0,
    )


def test_gen_code_instance_v0_zero_default():
    ic_obj = iscc_core.code_instance.gen_instance_code_v0(BytesIO(b"\x00"))
    assert ic_obj == dict(
        iscc="ISCC:IAAS2OW637YRWYPR",
        datahash="bdyqc2ow637yrwyprjseg4nnpua3hg3onq6tu2j5vyfiqejoq6wjoeey",
        filesize=1,
    )


def test_gen_code_instance_v0_hello_world_128():
    ic_obj = iscc_core.code_instance.gen_instance_code_v0(BytesIO(b"hello world"), 128)
    assert ic_obj == dict(
        iscc="ISCC:IAB5OSMB56TQUDEIBOGYYGMF2B25W",
        datahash="bdyqnosmb56tqudeibogyygmf2b25xs7wpg4zux4zcts2v6llqmnj4ja",
        filesize=11,
    )


def test_gen_code_instance_hello_world_256():
    ic_obj = iscc_core.code_instance.gen_instance_code(BytesIO(b"hello world"), 256)
    assert ic_obj == dict(
        iscc="ISCC:IAD5OSMB56TQUDEIBOGYYGMF2B25XS7WPG4ZUX4ZCTS2V6LLQMNJ4JA",
        datahash="bdyqnosmb56tqudeibogyygmf2b25xs7wpg4zux4zcts2v6llqmnj4ja",
        filesize=11,
    )


def test_gen_instance_code_schema_conformance():
    iscc_obj = ISCC(**iscc_core.gen_instance_code_v0(BytesIO(b"hello world")))
    assert iscc_obj.iscc == "ISCC:IAA5OSMB56TQUDEI"
