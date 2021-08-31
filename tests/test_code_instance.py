from io import BytesIO
from iscc_core import code_instance


def test_hash_instance_empty():
    assert (
        code_instance.hash_instance(BytesIO(b"")).hex()
        == "af1349b9f5f9a1a6a0404dea36dcc9499bcb25c9adc112b7cc9a93cae41f3262"
    )


def test_hash_instance_zero():
    assert (
        code_instance.hash_instance(BytesIO(b"\x00")).hex()
        == "2d3adedff11b61f14c886e35afa036736dcd87a74d27b5c1510225d0f592e213"
    )
