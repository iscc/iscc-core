from io import BytesIO
import random
from iscc_core import code_data
from iscc_core.options import opts
from tests.utils import static_bytes

MB1 = 1024 * 1024
TEST_DATA = static_bytes(MB1)


def test_data_granular_default_false():
    assert opts.data_granular is False


def test_hash_data_v0_granular_false():
    digest = code_data.soft_hash_data_v0(BytesIO(TEST_DATA), granular=False)
    assert (
        digest.hex()
        == "e5b3daf1118cf09cb5c5ac323a9f68ca04465f9e3942297ebd1e6360f5bb98df"
    )


def test_hash_data_v0_granular_true():
    digest, features, sizes = code_data.soft_hash_data_v0(
        BytesIO(TEST_DATA), granular=True
    )
    assert (
        digest.hex()
        == "e5b3daf1118cf09cb5c5ac323a9f68ca04465f9e3942297ebd1e6360f5bb98df"
    )
    assert features == [
        "_kS7wD4kvsA",
        "_3GTQp7AlgQ",
        "-TjPB2hxj00",
        "ZQ7hpcaKqA0",
        "nnn0C0IL28U",
        "OCAg9xyUc00",
        "zB5L4U7zNI0",
        "_mMAKFQMTwQ",
        "TBV2kckb4Fw",
        "odjLbH8MaKw",
        "8Opao8TnUz0",
        "t-i8q4sN6D0",
        "tvM5jXLG8J4",
        "xtv501iHqxs",
        "67pRxkkBFrE",
        "-PwAa5vR6J8",
    ]
    assert sizes == [
        71849,
        62221,
        69584,
        69566,
        63983,
        61275,
        65034,
        67510,
        64578,
        67387,
        66604,
        61790,
        70521,
        64208,
        61343,
        61123,
    ]


def test_hash_data_v0_empty():
    digest = code_data.soft_hash_data_v0(BytesIO(b""), granular=False)
    assert (
        digest.hex()
        == "25f0bab671f506e1c532f892d9d7917a252e7a520832f5963a8cd4e9a7e312b5"
    )


def test_hash_data_v0_empty_granular():
    digest, features, sizes = code_data.soft_hash_data_v0(BytesIO(b""), granular=True)
    assert (
        digest.hex()
        == "25f0bab671f506e1c532f892d9d7917a252e7a520832f5963a8cd4e9a7e312b5"
    )
    assert features == ["JfC6tnH1BuE"]
    assert sizes == [0]


def test_hash_data_v0_zero():
    digest = code_data.soft_hash_data_v0(BytesIO(b"\x00"))
    assert (
        digest.hex()
        == "770f8fd225ec1e5abb95e406afaddef303defe2f0d03b74c388f7b42ef96c7af"
    )


def test_hash_data_v0_zero_granular():
    digest, features, sizes = code_data.soft_hash_data_v0(
        BytesIO(b"\x00"), granular=True
    )
    assert (
        digest.hex()
        == "770f8fd225ec1e5abb95e406afaddef303defe2f0d03b74c388f7b42ef96c7af"
    )
    assert features == ["dw-P0iXsHlo"]
    assert sizes == [1]


def test_gen_code_data_v0_default():
    dc_obj = code_data.gen_data_code_v0(BytesIO(TEST_DATA))
    assert dc_obj == dict(code="GAA6LM626EIYZ4E4", features=None, sizes=None)


def test_gen_code_data_v0_granular():
    dc_obj = code_data.gen_data_code_v0(BytesIO(TEST_DATA), granular=True)
    assert dc_obj == dict(
        code="GAA6LM626EIYZ4E4",
        features=[
            "_kS7wD4kvsA",
            "_3GTQp7AlgQ",
            "-TjPB2hxj00",
            "ZQ7hpcaKqA0",
            "nnn0C0IL28U",
            "OCAg9xyUc00",
            "zB5L4U7zNI0",
            "_mMAKFQMTwQ",
            "TBV2kckb4Fw",
            "odjLbH8MaKw",
            "8Opao8TnUz0",
            "t-i8q4sN6D0",
            "tvM5jXLG8J4",
            "xtv501iHqxs",
            "67pRxkkBFrE",
            "-PwAa5vR6J8",
        ],
        sizes=[
            71849,
            62221,
            69584,
            69566,
            63983,
            61275,
            65034,
            67510,
            64578,
            67387,
            66604,
            61790,
            70521,
            64208,
            61343,
            61123,
        ],
    )


def test_DataHasherV0_single_shot():
    hasher = code_data.DataHasherV0(TEST_DATA)
    assert (
        hasher.digest().hex()
        == "e5b3daf1118cf09cb5c5ac323a9f68ca04465f9e3942297ebd1e6360f5bb98df"
    )


def test_DataHasherV0_stream_push():
    stream = BytesIO(TEST_DATA)
    hasher = code_data.DataHasherV0()
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
    hasher = code_data.DataHasherV0(chunk)
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
    h1 = code_data.soft_hash_data_v0(BytesIO(ba)).hex()
    assert h1 == "e5b3daf1118cf09cb5c5ac323a9f68ca04465f9e3942297ebd1e6360f5bb98df"
    for x in range(9):
        ba.insert(rpos(), rbyte())
        assert code_data.soft_hash_data_v0(BytesIO(ba)).hex() == h1

    # 1-bit difference on 10th byte change
    ba.insert(rpos(), rbyte())
    h2 = code_data.soft_hash_data_v0(BytesIO(ba)).hex()
    assert h1 != h2


def test_DataHasher():
    assert code_data.DataHasher(TEST_DATA).digest() == code_data.soft_hash_data_v0(
        BytesIO(TEST_DATA)
    )
