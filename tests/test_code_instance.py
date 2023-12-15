from io import BytesIO
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
        datahash="1e20af1349b9f5f9a1a6a0404dea36dcc9499bcb25c9adc112b7cc9a93cae41f3262",
        filesize=0,
    )


def test_gen_code_instance_v0_zero_default():
    ic_obj = iscc_core.code_instance.gen_instance_code_v0(BytesIO(b"\x00"))
    assert ic_obj == dict(
        iscc="ISCC:IAAS2OW637YRWYPR",
        datahash="1e202d3adedff11b61f14c886e35afa036736dcd87a74d27b5c1510225d0f592e213",
        filesize=1,
    )


def test_gen_code_instance_v0_hello_world_128():
    ic_obj = iscc_core.code_instance.gen_instance_code_v0(BytesIO(b"hello world"), 128)
    assert ic_obj == dict(
        iscc="ISCC:IAB5OSMB56TQUDEIBOGYYGMF2B25W",
        datahash="1e20d74981efa70a0c880b8d8c1985d075dbcbf679b99a5f9914e5aaf96b831a9e24",
        filesize=11,
    )


def test_gen_code_instance_hello_world_256():
    ic_obj = iscc_core.code_instance.gen_instance_code(BytesIO(b"hello world"), 256)
    assert ic_obj == dict(
        iscc="ISCC:IAD5OSMB56TQUDEIBOGYYGMF2B25XS7WPG4ZUX4ZCTS2V6LLQMNJ4JA",
        datahash="1e20d74981efa70a0c880b8d8c1985d075dbcbf679b99a5f9914e5aaf96b831a9e24",
        filesize=11,
    )


def test_gen_instance_code_schema_conformance():
    iscc_obj = iscc_core.gen_instance_code_v0(BytesIO(b"hello world"))
    assert iscc_obj == {
        "iscc": "ISCC:IAA5OSMB56TQUDEI",
        "datahash": "1e20d74981efa70a0c880b8d8c1985d075dbcbf679b99a5f9914e5aaf96b831a9e24",
        "filesize": 11,
    }
