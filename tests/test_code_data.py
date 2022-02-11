from io import BytesIO
import random

from iscc_schema.schema import ISCC

import iscc_core


def test_hash_data_v0(static_bytes):
    digest = iscc_core.code_data.soft_hash_data_v0(BytesIO(static_bytes))
    assert digest.hex() == "e5b3daf1118cf09cb5c5ac323a9f68ca04465f9e3942297ebd1e6360f5bb98df"


def test_hash_data_v0_empty():
    digest = iscc_core.code_data.soft_hash_data_v0(BytesIO(b""))
    assert digest.hex() == "25f0bab671f506e1c532f892d9d7917a252e7a520832f5963a8cd4e9a7e312b5"


def test_hash_data_v0_zero():
    digest = iscc_core.code_data.soft_hash_data_v0(BytesIO(b"\x00"))
    assert digest.hex() == "770f8fd225ec1e5abb95e406afaddef303defe2f0d03b74c388f7b42ef96c7af"


def test_gen_code_data_v0_default(static_bytes):
    dc_obj = iscc_core.code_data.gen_data_code_v0(BytesIO(static_bytes))
    assert dc_obj == dict(iscc="ISCC:GAA6LM626EIYZ4E4")


def test_gen_code_data_default(static_bytes):
    dc_obj = iscc_core.code_data.gen_data_code(BytesIO(static_bytes))
    assert dc_obj == dict(iscc="ISCC:GAA6LM626EIYZ4E4")


def test_DataHasherV0_single_shot(static_bytes):
    hasher = iscc_core.code_data.DataHasherV0(static_bytes)
    assert (
        hasher.digest().hex() == "e5b3daf1118cf09cb5c5ac323a9f68ca04465f9e3942297ebd1e6360f5bb98df"
    )


def test_DataHasherV0_stream_push(static_bytes):
    stream = BytesIO(static_bytes)
    hasher = iscc_core.code_data.DataHasherV0()
    chunk = stream.read(2048)
    while chunk:
        hasher.push(chunk)
        chunk = stream.read(2048)
    assert (
        hasher.digest().hex() == "e5b3daf1118cf09cb5c5ac323a9f68ca04465f9e3942297ebd1e6360f5bb98df"
    )


def test_DataHasherV0_mixed(static_bytes):
    stream = BytesIO(static_bytes)
    chunk = stream.read(2048)
    hasher = iscc_core.code_data.DataHasherV0(chunk)
    chunk = stream.read(2048)
    while chunk:
        hasher.push(chunk)
        chunk = stream.read(2048)
    assert (
        hasher.digest().hex() == "e5b3daf1118cf09cb5c5ac323a9f68ca04465f9e3942297ebd1e6360f5bb98df"
    )


def test_hash_data_1mib_robust(static_bytes):
    ba = bytearray(static_bytes)

    random.seed(1)
    rbyte = lambda: random.randint(0, 256)
    rpos = lambda: random.randint(0, 1024 * 1024)

    # 9 random single byte changes in data
    h1 = iscc_core.code_data.soft_hash_data_v0(BytesIO(ba)).hex()
    assert h1 == "e5b3daf1118cf09cb5c5ac323a9f68ca04465f9e3942297ebd1e6360f5bb98df"
    for _ in range(9):
        ba.insert(rpos(), rbyte())
        assert iscc_core.code_data.soft_hash_data_v0(BytesIO(ba)).hex() == h1

    # 1-bit difference on 10th byte change
    ba.insert(rpos(), rbyte())
    h2 = iscc_core.code_data.soft_hash_data_v0(BytesIO(ba)).hex()
    assert h1 != h2


def test_DataHasher(static_bytes):
    assert iscc_core.code_data.DataHasher(
        static_bytes
    ).digest() == iscc_core.code_data.soft_hash_data_v0(BytesIO(static_bytes))


def test_gen_data_code_schema_conformance():
    iscc_obj = ISCC(**iscc_core.gen_data_code_v0(BytesIO(b"\xff")))
    assert iscc_obj.iscc == "ISCC:GAAV5ZIQC4WCUBIK"
