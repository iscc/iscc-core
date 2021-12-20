# -*- coding: utf-8 -*-
import os
from binascii import unhexlify
import pytest
from bitarray import bitarray as ba, frozenbitarray
import iscc_core


def test_main_type():
    assert isinstance(iscc_core.codec.MT.META, int)
    assert iscc_core.codec.MT.META == 0


def test_write_header():
    with pytest.raises(AssertionError):
        iscc_core.codec.write_header(0, 0, 0, 0)
    assert iscc_core.codec.write_header(0, 0, 0, 32) == bytes(
        [0b0000_0000, 0b0000_0000]
    )
    assert iscc_core.codec.write_header(1, 0, 0, 32) == bytes(
        [0b0001_0000, 0b0000_0000]
    )
    assert iscc_core.codec.write_header(7, 1, 1, 64) == bytes(
        [0b0111_0001, 0b0001_0001]
    )
    assert iscc_core.codec.write_header(8, 1, 1, 64) == bytes(
        [0b1000_0000, 0b0001_0001, 0b0001_0000]
    )
    assert iscc_core.codec.write_header(8, 8, 1, 64) == bytes(
        [0b1000_0000, 0b1000_0000, 0b0001_0001]
    )


def test_read_header():
    rh = iscc_core.codec.read_header
    assert rh(bytes([0b0000_0000, 0b0000_0000])) == (0, 0, 0, 32, b"")
    assert rh(bytes([0b0000_0000, 0b0000_0000, 0b0000_0000])) == (0, 0, 0, 32, b"\x00")
    assert rh(bytes([0b0001_0000, 0b0000_0000])) == (1, 0, 0, 32, b"")
    assert rh(bytes([0b0111_0001, 0b0001_0001])) == (7, 1, 1, 64, b"")
    assert rh(bytes([0b1000_0000, 0b0001_0001, 0b0001_0000])) == (8, 1, 1, 64, b"")
    assert rh(bytes([0b1000_0000, 0b1000_0000, 0b0001_0001])) == (8, 8, 1, 64, b"")


def test_encode_base32():
    assert iscc_core.codec.encode_base32(b"") == ""
    assert iscc_core.codec.encode_base32(b"f") == "MY"
    assert iscc_core.codec.encode_base32(b"fo") == "MZXQ"
    assert iscc_core.codec.encode_base32(b"foo") == "MZXW6"
    assert iscc_core.codec.encode_base32(b"foob") == "MZXW6YQ"
    assert iscc_core.codec.encode_base32(b"fooba") == "MZXW6YTB"
    assert iscc_core.codec.encode_base32(b"foobar") == "MZXW6YTBOI"


def test_decode_base32():
    assert iscc_core.codec.decode_base32("") == b""
    assert iscc_core.codec.decode_base32("MY") == b"f"
    assert iscc_core.codec.decode_base32("My") == b"f"
    assert iscc_core.codec.decode_base32("my") == b"f"
    assert iscc_core.codec.decode_base32("MZXQ") == b"fo"
    assert iscc_core.codec.decode_base32("MZXW6") == b"foo"
    assert iscc_core.codec.decode_base32("MZXW6YQ") == b"foob"
    assert iscc_core.codec.decode_base32("MZXW6YTB") == b"fooba"
    assert iscc_core.codec.decode_base32("MZXW6YTBOI") == b"foobar"


def test_decode_base_64():
    data = os.urandom(8)
    enc = iscc_core.codec.encode_base64(data)
    assert iscc_core.codec.decode_base64(enc) == data


def test_write_varnibble():
    with pytest.raises(ValueError):
        iscc_core.codec._write_varnibble(-1)
    assert iscc_core.codec._write_varnibble(0) == ba("0000")
    assert iscc_core.codec._write_varnibble(7) == ba("0111")
    assert iscc_core.codec._write_varnibble(8) == ba("10000000")
    assert iscc_core.codec._write_varnibble(9) == ba("10000001")
    assert iscc_core.codec._write_varnibble(71) == ba("10111111")
    assert iscc_core.codec._write_varnibble(72) == ba("110000000000")
    assert iscc_core.codec._write_varnibble(73) == ba("110000000001")
    assert iscc_core.codec._write_varnibble(583) == ba("110111111111")
    assert iscc_core.codec._write_varnibble(584) == ba("1110000000000000")
    assert iscc_core.codec._write_varnibble(4679) == ba("1110111111111111")
    with pytest.raises(ValueError):
        iscc_core.codec._write_varnibble(4680)
    with pytest.raises(TypeError):
        iscc_core.codec._write_varnibble(1.0)


def test_read_varnibble():
    with pytest.raises(ValueError):
        iscc_core.codec._read_varnibble(ba("0"))
    with pytest.raises(ValueError):
        iscc_core.codec._read_varnibble(ba("1"))
    with pytest.raises(ValueError):
        iscc_core.codec._read_varnibble(ba("011"))
    with pytest.raises(ValueError):
        iscc_core.codec._read_varnibble(ba("100"))
    assert iscc_core.codec._read_varnibble(ba("0000")) == (0, ba())
    assert iscc_core.codec._read_varnibble(ba("000000")) == (0, ba("00"))
    assert iscc_core.codec._read_varnibble(ba("0111")) == (7, ba())
    assert iscc_core.codec._read_varnibble(ba("01110")) == (7, ba("0"))
    assert iscc_core.codec._read_varnibble(ba("01111")) == (7, ba("1"))
    assert iscc_core.codec._read_varnibble(ba("10000000")) == (8, ba())
    assert iscc_core.codec._read_varnibble(ba("10000001")) == (9, ba())
    assert iscc_core.codec._read_varnibble(ba("10000001110")) == (9, ba("110"))
    assert iscc_core.codec._read_varnibble(ba("10111111")) == (71, ba())
    assert iscc_core.codec._read_varnibble(ba("101111110")) == (71, ba("0"))
    assert iscc_core.codec._read_varnibble(ba("110000000000")) == (72, ba())
    assert iscc_core.codec._read_varnibble(ba("11000000000010")) == (72, ba("10"))
    assert iscc_core.codec._read_varnibble(ba("110000000001")) == (73, ba())
    assert iscc_core.codec._read_varnibble(ba("110000000001010")) == (73, ba("010"))
    assert iscc_core.codec._read_varnibble(ba("110111111111")) == (583, ba())
    assert iscc_core.codec._read_varnibble(ba("1101111111111010")) == (583, ba("1010"))
    assert iscc_core.codec._read_varnibble(ba("1110000000000000")) == (584, ba())
    assert iscc_core.codec._read_varnibble(ba("111000000000000001010")) == (
        584,
        ba("01010"),
    )
    assert iscc_core.codec._read_varnibble(ba("1110111111111111")) == (4679, ba())
    assert iscc_core.codec._read_varnibble(ba("1110111111111111101010")) == (
        4679,
        ba("101010"),
    )


def test_iscc_clean():
    assert iscc_core.codec.clean("somecode") == "somecode"
    assert iscc_core.codec.clean("ISCC: SOME-CODE") == "SOMECODE"
    assert iscc_core.codec.clean(" SOMECODE ") == "SOMECODE"
    assert iscc_core.codec.clean("ISCC:") == ""


def test_code_properties():
    c64 = iscc_core.codec.Code(iscc_core.gen_meta_code("Hello World").iscc)
    c256 = iscc_core.codec.Code(iscc_core.gen_meta_code("Hello World", bits=256).iscc)
    assert c64.code == "AAA77PPFVS6JDUQB"
    assert c256.code == "AAD77PPFVS6JDUQBWZDBIUGOUNAGIZYGCQ75ICNLH5QV73OXGWZV5CQ"
    assert c64.bytes == unhexlify(c64.hex)
    assert c64.type_id == "META-NONE-V0-64"
    assert c64.explain == "META-NONE-V0-64-" + c64.hash_hex
    assert isinstance(c64.hash_ints[0], int)
    assert c64.hash_bits == "".join(str(i) for i in c64.hash_ints)
    assert c256.hash_bits == "".join(str(i) for i in c256.hash_ints)
    assert c64.hash_uint == 18428137780330746369
    assert (
        c256.hash_uint
        == 115675295640858983304133651543519403601786105490037992581561449255353963470474
    )
    assert c64.maintype == iscc_core.codec.MT.META
    assert c64.maintype == 0
    assert c64.subtype == iscc_core.codec.ST.NONE
    assert c64.subtype == 0
    assert c64.version == iscc_core.codec.VS.V0
    assert c64.length == 64
    assert c256.length == 256
    assert c64 ^ c64 == 0
    with pytest.raises(ValueError):
        _ = c64 ^ c256
    assert c64 == iscc_core.codec.Code(c64.bytes)
    assert c64 == iscc_core.codec.Code(c64.code)
    assert c64 == iscc_core.codec.Code(tuple(c64))
    assert isinstance(c64.hash_ba, frozenbitarray)


def test_code_hashable():
    code = iscc_core.codec.Code.rnd()
    assert code in {code}


def test_decompose_single_component():
    code = iscc_core.codec.Code.rnd(iscc_core.codec.MT.META)
    # assert c.decompose(code)[0] == code
    assert iscc_core.codec.decompose(code.code)[0] == code.code
    # assert c.decompose(code.bytes)[0] == code


def test_decompose_str_of_codes():
    mco = iscc_core.codec.Code.rnd(iscc_core.codec.MT.META)
    cco = iscc_core.codec.Code.rnd(iscc_core.codec.MT.CONTENT)
    dco = iscc_core.codec.Code.rnd(iscc_core.codec.MT.DATA)
    ico = iscc_core.codec.Code.rnd(iscc_core.codec.MT.INSTANCE)
    iscc = f"ISCC:{mco.code}-{cco.code}-{dco.code}-{ico.code}"
    codes = iscc_core.codec.decompose(iscc)
    assert codes == [mco.code, cco.code, dco.code, ico.code]


def test_Code_uri():
    mco = iscc_core.gen_meta_code("This is an URI representation of a Meta-Code")
    assert mco.code_obj.code == "AAARFRYHMQI6KPP6"
    assert mco.code_obj.uri == "iscc:aaarfryhmqi6kpp6"


def test_Code_mf_base32():
    mco = iscc_core.gen_meta_code("Hello base32")
    assert mco.code_obj.code == "AAAW277H32PJOVML"
    assert mco.code_obj.mf_base32 == "bzqaqaalnp7t55huxkwfq"


def test_Code_mf_base64url():
    mco = iscc_core.gen_meta_code("This is a base64url encoded Meta-Code")
    assert mco.code_obj.code == "AAARQFT7MCK4LPO7"
    assert mco.code_obj.mf_base64url == "uzAEAARgWf2CVxb3f"


def test_Code_raises():
    with pytest.raises(ValueError):
        iscc_core.codec.Code(13)


def test_Code_Code():
    code = iscc_core.codec.Code.rnd(iscc_core.codec.MT.META)
    assert iscc_core.codec.Code(code) == code


def test_Code_str_repr():
    mco = iscc_core.gen_meta_code("Hello str")
    assert mco.code_obj.code == "AAAWOMHEVMWZ2EYF"
    assert str(mco.code_obj) == "AAAWOMHEVMWZ2EYF"
    assert repr(mco.code_obj) == 'Code("AAAWOMHEVMWZ2EYF")'
    assert (
        bytes(mco.code_obj).hex() == "00016730e4ab2d9d1305" == mco.code_obj.bytes.hex()
    )
