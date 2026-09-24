# -*- coding: utf-8 -*-
"""Tests for the ISCC-SEQ codec (IEP-0020, C2PA soft binding values)."""

import base64
import io

import pytest

import iscc_core as ic
from iscc_core.constants import MC_PREFIX, MT

UNITS = [
    "ISCC:AADVPDD4R6733NMPFH3D57VTQ4KVH6VHL74XIWGUT37V5ZG56NV3NSI",
    "ISCC:EAD2RASIYU5IKLENP2OFI4CHZGRWYQCSW2WKX3Y6FJGOCXSYNYGLGBI",
    "ISCC:GADQLNA7GRZESMRF2J7NZPNWGI3II2ST5YUN5SS6GVQ2ZQGJXPPYDNI",
    "ISCC:IAD2KIVPJIWJZP3KQCESJL6SVT5APEZUPOJWM6HVTAXCF7OT3VFA4NY",
]

HEX = (
    "0007578c7c8fbfbdb58f29f63efeb3871553faa75ff97458d49eff5ee4ddf36bb6c92007a88248c53a852c8d"
    "7e9c547047c9a36c4052b6acabef1e2a4ce15e586e0cb305300705b41f3472493225d27edcbdb63236846a53"
    "ee28deca5e3561acc0c9bbdf81b54007a522af4a2c9cbf6a808924afd2acfa0793347b936678f5982e22fdd3"
    "dd4a0e37"
)

B64 = (
    "AAdXjHyPv721jyn2Pv6zhxVT+qdf+XRY1J7/XuTd82u2ySAHqIJIxTqFLI1+nFRwR8mjbEBStqyr7x4qTOFeWG4M"
    "swUwBwW0HzRySTIl0n7cvbYyNoRqU+4o3speNWGswMm734G1QAelIq9KLJy/aoCJJK/SrPoHkzR7k2Z49ZguIv3T"
    "3UoONw=="
)

TEXT = (
    "ISCC:AADVPDD4R6733NMPFH3D57VTQ4KVH6VHL74XIWGUT37V5ZG56NV3NSJAA6UIESGFHKCSZDL6TRKHAR6JUNWE"
    "AUVWVSV66HRKJTQV4WDOBSZQKMAHAW2B6NDSJEZCLUT63S63MMRWQRVFH3RI33FF4NLBVTAMTO67QG2UAB5FEKXUU"
    "LE4X5VIBCJEV7JKZ6QHSM2HXE3GPD2ZQLRC7XJ52SQOG4"
)

SINGLE_HEX = "2007a88248c53a852c8d7e9c547047c9a36c4052b6acabef1e2a4ce15e586e0cb305"

UNITS_128 = ["ISCC:GABQLNA7GRZESMRF2J7NZPNWGI3II", "ISCC:IAB2KIVPJIWJZP3KQCESJL6SVT5AO"]
HEX_128 = "300305b41f3472493225d27edcbdb63236844003a522af4a2c9cbf6a808924afd2acfa07"

UNITS_MIXED = ["ISCC:EEAYYNMFG5XOELK2", "ISCC:EIBZ6B7T76PAAYP7H334X77754376", UNITS[2]]
HEX_MIXED = (
    "21018c3585376ee22d5a22039f07f3ff9e0061ff3ef7cbffffef37ff300705b41f3472493225d27edcbdb632"
    "36846a53ee28deca5e3561acc0c9bbdf81b5"
)

ISCC_CODE_HEX = "5005578c7c8fbfbdb58fa88248c53a852c8d05b41f3472493225a522af4a2c9cbf6a"
ISCC_ID_HEX = "60100000000000000000"


def test_iep_example():
    value = ic.encode_seq(UNITS)
    query = base64.b64encode(value).decode("ascii")
    assert ic.decode_seq(value) == UNITS
    assert ic.decode_seq(base64.b64decode(query)) == UNITS
    text = "ISCC:" + ic.encode_base32(value)
    assert text == TEXT


def test_encode_seq_vector_1():
    value = ic.encode_seq(UNITS)
    assert len(value) == 136
    assert value.hex() == HEX
    assert base64.b64encode(value).decode("ascii") == B64
    assert len(ic.encode_base32(value)) == 218


def test_decode_seq_vector_1():
    assert ic.decode_seq(bytes.fromhex(HEX)) == UNITS
    assert ic.decode_seq(base64.b64decode(B64)) == UNITS


def test_decode_seq_bytes_like():
    raw = bytes.fromhex(HEX)
    assert ic.decode_seq(bytearray(raw)) == UNITS
    assert ic.decode_seq(memoryview(raw)) == UNITS


def test_seq_single_unit():
    unit = UNITS[1]
    value = ic.encode_seq([unit])
    assert value == ic.decode_base32(ic.iscc_clean(unit))
    assert value.hex() == SINGLE_HEX
    assert ic.decode_seq(value) == [unit]


def test_seq_two_128_bit_units():
    value = ic.encode_seq(UNITS_128)
    assert value.hex() == HEX_128
    assert ic.decode_seq(value) == UNITS_128


def test_seq_mixed_lengths_vector_2():
    value = ic.encode_seq(UNITS_MIXED)
    assert value.hex() == HEX_MIXED
    assert ic.decode_seq(value) == UNITS_MIXED


def test_encode_seq_accepts_tuple_and_generator():
    assert ic.encode_seq(tuple(UNITS)).hex() == HEX
    assert ic.encode_seq(u for u in UNITS).hex() == HEX


def test_encode_seq_tolerant_input():
    bare = [u.removeprefix("ISCC:") for u in UNITS]
    lower = [u.lower() for u in UNITS]
    bare_lower = [u.lower() for u in bare]
    hyphen = [u[:9] + "-" + u[9:] for u in UNITS]
    for variant in (bare, lower, bare_lower, hyphen):
        assert ic.encode_seq(variant).hex() == HEX


@pytest.mark.parametrize(
    "unit",
    ["ISCC:FAAAAAAAAAAA", "iscc:faaa-aaaaaaaa", "FAAA-AAAAAAAA", "faaaaaaaaaaa", "faaa-aaaaaaaa"],
)
def test_encode_seq_multibase_like_content(unit):
    assert ic.encode_seq([unit]).hex() == "28000000000000"


def test_encode_seq_multibase_like_meta():
    assert ic.encode_seq(["baaa-aaaaaaaa"]).hex() == "08000000000000"


@pytest.mark.parametrize("mt", [MT.META, MT.SEMANTIC, MT.CONTENT, MT.DATA, MT.INSTANCE])
@pytest.mark.parametrize("ln", range(8))
def test_seq_all_lengths_roundtrip(mt, ln):
    raw = ic.encode_header(mt, 0, 0, ln) + bytes(range(4 * (ln + 1)))
    units = ic.decode_seq(raw)
    assert len(units) == 1
    assert ic.encode_seq(units) == raw


@pytest.mark.parametrize("st", [7, 8, 71, 72, 583, 584, 4679])
@pytest.mark.parametrize("vs", [0, 1])
def test_seq_unknown_subtype_version_roundtrip(st, vs):
    raw = ic.encode_header(MT.CONTENT, st, vs, 7) + bytes(range(32))
    units = ic.decode_seq(raw)
    assert ic.encode_seq(units) == raw
    bare = units[0].removeprefix("ISCC:")
    hyphen = bare[:4] + "-" + bare[4:]
    for variant in (bare, bare.lower(), hyphen, hyphen.lower()):
        assert ic.encode_seq([variant]) == raw


def test_decode_seq_undefined_subtype():
    assert ic.decode_seq(bytes.fromhex("270000000000")) == ["ISCC:E4AAAAAAAA"]


def test_seq_interop_with_iscc_decompose():
    value = ic.encode_seq(UNITS)
    decomposed = ic.iscc_decompose("ISCC:" + ic.encode_base32(value))
    assert decomposed == [u.removeprefix("ISCC:") for u in UNITS]


def test_seq_repeated_keys_keep_order():
    data_64 = ic.gen_data_code_v0(io.BytesIO(b"a"), 64)["iscc"]
    data_256 = ic.gen_data_code_v0(io.BytesIO(b"a"), 256)["iscc"]
    inst_64 = ic.gen_instance_code_v0(io.BytesIO(b"a"), 64)["iscc"]
    inst_256 = ic.gen_instance_code_v0(io.BytesIO(b"a"), 256)["iscc"]
    units = [data_256, inst_64, data_64, inst_256]
    assert ic.decode_seq(ic.encode_seq(units)) == units


def test_decode_seq_empty():
    with pytest.raises(ValueError, match="Empty"):
        ic.decode_seq(b"")


def test_decode_seq_incomplete_header():
    with pytest.raises(ValueError, match="Malformed ISCC-HEADER at offset 0"):
        ic.decode_seq(bytes.fromhex("28"))


def test_decode_seq_nonzero_header_padding():
    assert ic.decode_seq(bytes.fromhex("28000000000000")) == ["ISCC:FAAAAAAAAAAA"]
    with pytest.raises(ValueError, match="Non-canonical ISCC-HEADER at offset 0"):
        ic.decode_seq(bytes.fromhex("28000100000000"))


def test_decode_seq_nonzero_header_padding_second_unit():
    raw = bytes.fromhex(SINGLE_HEX + "28000100000000")
    with pytest.raises(ValueError, match=f"offset {len(bytes.fromhex(SINGLE_HEX))}"):
        ic.decode_seq(raw)


@pytest.mark.parametrize("ln", [8, 9])
def test_decode_seq_length_above_7(ln):
    raw = ic.encode_header(MT.CONTENT, 0, 0, ln) + bytes(4 * (ln + 1))
    with pytest.raises(ValueError, match=f"Unsupported Length field {ln}"):
        ic.decode_seq(raw)


def test_decode_seq_truncated():
    with pytest.raises(ValueError, match="Truncated ISCC-UNIT at offset 102"):
        ic.decode_seq(bytes.fromhex(HEX)[:-1])


def test_decode_seq_trailing_byte():
    with pytest.raises(ValueError, match="offset 136"):
        ic.decode_seq(bytes.fromhex(HEX) + bytes(1))


@pytest.mark.parametrize(
    "raw",
    [
        bytes.fromhex(ISCC_CODE_HEX),
        bytes.fromhex(ISCC_ID_HEX),
        ic.encode_header(MT.FLAKE, 0, 0, 1) + bytes(8),
    ],
)
def test_decode_seq_rejects_maintype(raw):
    with pytest.raises(ValueError, match="not permitted"):
        ic.decode_seq(raw)


@pytest.mark.parametrize("data", [6, UNITS[0], [0, 1, 2], None])
def test_decode_seq_type_error(data):
    with pytest.raises(TypeError):
        ic.decode_seq(data)


@pytest.mark.parametrize("units", [UNITS[0], bytes.fromhex(HEX), [b"AAAA"], [None]])
def test_encode_seq_type_error(units):
    with pytest.raises(TypeError):
        ic.encode_seq(units)


def test_encode_seq_empty():
    with pytest.raises(ValueError, match="at least one"):
        ic.encode_seq([])


@pytest.mark.parametrize("unit", ["", "  "])
def test_encode_seq_empty_unit(unit):
    with pytest.raises(ValueError, match="must not be empty"):
        ic.encode_seq([unit])


@pytest.mark.parametrize("hex_code", [ISCC_CODE_HEX, ISCC_ID_HEX])
def test_encode_seq_rejects_maintype(hex_code):
    unit = "ISCC:" + ic.encode_base32(bytes.fromhex(hex_code))
    with pytest.raises(ValueError, match="not permitted"):
        ic.encode_seq([unit])


def test_encode_seq_rejects_flake():
    flake = ic.gen_flake_code_v0()["iscc"]
    with pytest.raises(ValueError, match="not permitted"):
        ic.encode_seq([flake])


def test_encode_seq_rejects_multiformat():
    raw = ic.decode_base32(ic.iscc_clean(UNITS[0]))
    for mf in ("f" + (MC_PREFIX + raw).hex(), "b" + ic.encode_base32(MC_PREFIX + raw).lower()):
        with pytest.raises(ValueError):
            ic.encode_seq([mf])


def test_encode_seq_trailing_data():
    with pytest.raises(ValueError, match="Trailing data"):
        ic.encode_seq([ic.encode_base32(bytes(8))])


def test_encode_seq_multiple_units_in_one_string():
    with pytest.raises(ValueError, match="Trailing data"):
        ic.encode_seq([TEXT])


def test_read_unit_default_offset():
    raw = bytes.fromhex(SINGLE_HEX)
    assert ic.read_unit(raw) == len(raw)


def test_read_unit_sequential_offsets():
    raw = bytes.fromhex(HEX)
    offsets = [0]
    while offsets[-1] < len(raw):
        offsets.append(ic.read_unit(raw, offsets[-1]))
    assert offsets == [0, 34, 68, 102, 136]


def test_read_unit_bytes_like():
    raw = bytes.fromhex(HEX_128)
    assert ic.read_unit(bytearray(raw)) == 18
    assert ic.read_unit(memoryview(raw), 18) == len(raw)


def test_read_unit_multibyte_memoryview():
    assert ic.read_unit(memoryview(bytes.fromhex("300000000000")).cast("H")) == 6
    raw = bytes.fromhex(HEX_128)
    assert ic.read_unit(memoryview(raw).cast("H"), 18) == 36
    assert ic.read_unit(memoryview(raw).cast("I"), 18) == 36


def test_read_unit_truncated_at_offset():
    raw = bytes.fromhex(HEX_128)[:-1]
    with pytest.raises(ValueError, match="Truncated ISCC-UNIT at offset 18"):
        ic.read_unit(raw, 18)
