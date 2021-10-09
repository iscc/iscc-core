from io import BytesIO
from iscc_core import code_instance


def test_hash_instance_v0_empty():
    assert (
        code_instance.hash_instance_v0(BytesIO(b"")).hex()
        == "af1349b9f5f9a1a6a0404dea36dcc9499bcb25c9adc112b7cc9a93cae41f3262"
    )


def test_hash_instance_v0_zero():
    assert (
        code_instance.hash_instance_v0(BytesIO(b"\x00")).hex()
        == "2d3adedff11b61f14c886e35afa036736dcd87a74d27b5c1510225d0f592e213"
    )


def test_code_instance_v0_empty_default():
    assert code_instance.gen_instance_code_v0(BytesIO(b"")) == "IAA26E2JXH27TING"


def test_code_instance_v0_zero_default():
    assert code_instance.gen_instance_code_v0(BytesIO(b"\x00")) == "IAAS2OW637YRWYPR"


def test_code_instance_v0_hello_world_128():
    assert (
        code_instance.gen_instance_code_v0(BytesIO(b"hello world"), 128)
        == "IAB5OSMB56TQUDEIBOGYYGMF2B25W"
    )
