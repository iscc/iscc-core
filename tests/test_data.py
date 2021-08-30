from io import BytesIO
import random
from iscc_core.data import hash_data, hash_data_v0, DataHasherV0, DataHasher
from tests.utils import static_bytes

MB1 = 1024 * 1024
TEST_DATA = static_bytes(MB1)


def test_hash_data():
    assert (
        hash_data(BytesIO(TEST_DATA)).hex()
        == "e5b3daf1118cf09cb5c5ac323a9f68ca04465f9e3942297ebd1e6360f5bb98df"
    )


def test_hash_data_v0_empty():
    assert (
        hash_data_v0(BytesIO(b"")).hex()
        == "25f0bab671f506e1c532f892d9d7917a252e7a520832f5963a8cd4e9a7e312b5"
    )


def test_hash_data_v0_zero():
    assert (
        hash_data_v0(BytesIO(b"\x00")).hex()
        == "770f8fd225ec1e5abb95e406afaddef303defe2f0d03b74c388f7b42ef96c7af"
    )


def test_hash_data_v0_1mb():
    assert (
        hash_data_v0(BytesIO(TEST_DATA)).hex()
        == "e5b3daf1118cf09cb5c5ac323a9f68ca04465f9e3942297ebd1e6360f5bb98df"
    )


def test_DataHasherV0_single_shot():
    hasher = DataHasherV0(TEST_DATA)
    assert (
        hasher.digest().hex()
        == "e5b3daf1118cf09cb5c5ac323a9f68ca04465f9e3942297ebd1e6360f5bb98df"
    )


def test_DataHasherV0_stream_push():
    stream = BytesIO(TEST_DATA)
    hasher = DataHasherV0()
    chunk = stream.read(2048)
    while chunk:
        hasher.push(chunk)
        chunk = stream.read(2048)
    assert (
        hasher.digest().hex()
        == "e5b3daf1118cf09cb5c5ac323a9f68ca04465f9e3942297ebd1e6360f5bb98df"
    )


def test_DataHasherV0_mixed():
    stream = BytesIO(TEST_DATA)
    chunk = stream.read(2048)
    hasher = DataHasherV0(chunk)
    chunk = stream.read(2048)
    while chunk:
        hasher.push(chunk)
        chunk = stream.read(2048)
    assert (
        hasher.digest().hex()
        == "e5b3daf1118cf09cb5c5ac323a9f68ca04465f9e3942297ebd1e6360f5bb98df"
    )


def test_hash_data_1mib_robust():
    ba = bytearray(TEST_DATA)

    random.seed(1)
    rbyte = lambda: random.randint(0, 256)
    rpos = lambda: random.randint(0, MB1)

    # 9 random single byte changes in data
    h1 = hash_data_v0(BytesIO(ba)).hex()
    assert h1 == "e5b3daf1118cf09cb5c5ac323a9f68ca04465f9e3942297ebd1e6360f5bb98df"
    for x in range(9):
        ba.insert(rpos(), rbyte())
        assert hash_data_v0(BytesIO(ba)).hex() == h1

    # 1-bit difference on 10th byte change
    ba.insert(rpos(), rbyte())
    h2 = hash_data_v0(BytesIO(ba)).hex()
    assert h1 != h2


def test_DataHasher():
    assert DataHasher(TEST_DATA).digest() == hash_data(BytesIO(TEST_DATA))
