# -*- coding: utf-8 -*-
import os
from binascii import unhexlify
import pytest
from bitarray import bitarray as ba, frozenbitarray
import iscc_core as ic


def test_main_type():
    assert isinstance(ic.codec.MT.META, int)
    assert ic.codec.MT.META == 0


def test_write_header():
    with pytest.raises(AssertionError):
        ic.codec.write_header(0, 0, 0, 0)
    assert ic.codec.write_header(0, 0, 0, 32) == bytes([0b0000_0000, 0b0000_0000])
    assert ic.codec.write_header(1, 0, 0, 32) == bytes([0b0001_0000, 0b0000_0000])
    assert ic.codec.write_header(7, 1, 1, 64) == bytes([0b0111_0001, 0b0001_0001])
    assert ic.codec.write_header(8, 1, 1, 64) == bytes(
        [0b1000_0000, 0b0001_0001, 0b0001_0000]
    )
    assert ic.codec.write_header(8, 8, 1, 64) == bytes(
        [0b1000_0000, 0b1000_0000, 0b0001_0001]
    )


def test_read_header():
    rh = ic.codec.read_header
    assert rh(bytes([0b0000_0000, 0b0000_0000])) == (0, 0, 0, 32, b"")
    assert rh(bytes([0b0000_0000, 0b0000_0000, 0b0000_0000])) == (0, 0, 0, 32, b"\x00")
    assert rh(bytes([0b0001_0000, 0b0000_0000])) == (1, 0, 0, 32, b"")
    assert rh(bytes([0b0111_0001, 0b0001_0001])) == (7, 1, 1, 64, b"")
    assert rh(bytes([0b1000_0000, 0b0001_0001, 0b0001_0000])) == (8, 1, 1, 64, b"")
    assert rh(bytes([0b1000_0000, 0b1000_0000, 0b0001_0001])) == (8, 8, 1, 64, b"")


def test_encode_base32():
    assert ic.codec.encode_base32(b"") == ""
    assert ic.codec.encode_base32(b"f") == "MY"
    assert ic.codec.encode_base32(b"fo") == "MZXQ"
    assert ic.codec.encode_base32(b"foo") == "MZXW6"
    assert ic.codec.encode_base32(b"foob") == "MZXW6YQ"
    assert ic.codec.encode_base32(b"fooba") == "MZXW6YTB"
    assert ic.codec.encode_base32(b"foobar") == "MZXW6YTBOI"


def test_decode_base32():
    assert ic.codec.decode_base32("") == b""
    assert ic.codec.decode_base32("MY") == b"f"
    assert ic.codec.decode_base32("My") == b"f"
    assert ic.codec.decode_base32("my") == b"f"
    assert ic.codec.decode_base32("MZXQ") == b"fo"
    assert ic.codec.decode_base32("MZXW6") == b"foo"
    assert ic.codec.decode_base32("MZXW6YQ") == b"foob"
    assert ic.codec.decode_base32("MZXW6YTB") == b"fooba"
    assert ic.codec.decode_base32("MZXW6YTBOI") == b"foobar"


def test_decode_base32_casefold():
    assert ic.decode_base32("MZXW6YTBOI") == ic.decode_base32("mZxW6ytBOI")


def test_decode_base_64():
    data = os.urandom(8)
    enc = ic.codec.encode_base64(data)
    assert ic.codec.decode_base64(enc) == data


def test_write_varnibble():
    with pytest.raises(ValueError):
        ic.codec.write_varnibble(-1)
    assert ic.codec.write_varnibble(0) == ba("0000")
    assert ic.codec.write_varnibble(7) == ba("0111")
    assert ic.codec.write_varnibble(8) == ba("10000000")
    assert ic.codec.write_varnibble(9) == ba("10000001")
    assert ic.codec.write_varnibble(71) == ba("10111111")
    assert ic.codec.write_varnibble(72) == ba("110000000000")
    assert ic.codec.write_varnibble(73) == ba("110000000001")
    assert ic.codec.write_varnibble(583) == ba("110111111111")
    assert ic.codec.write_varnibble(584) == ba("1110000000000000")
    assert ic.codec.write_varnibble(4679) == ba("1110111111111111")
    with pytest.raises(ValueError):
        ic.codec.write_varnibble(4680)
    with pytest.raises(TypeError):
        ic.codec.write_varnibble(1.0)


def test_read_varnibble():
    with pytest.raises(ValueError):
        ic.codec.read_varnibble(ba("0"))
    with pytest.raises(ValueError):
        ic.codec.read_varnibble(ba("1"))
    with pytest.raises(ValueError):
        ic.codec.read_varnibble(ba("011"))
    with pytest.raises(ValueError):
        ic.codec.read_varnibble(ba("100"))
    assert ic.codec.read_varnibble(ba("0000")) == (0, ba())
    assert ic.codec.read_varnibble(ba("000000")) == (0, ba("00"))
    assert ic.codec.read_varnibble(ba("0111")) == (7, ba())
    assert ic.codec.read_varnibble(ba("01110")) == (7, ba("0"))
    assert ic.codec.read_varnibble(ba("01111")) == (7, ba("1"))
    assert ic.codec.read_varnibble(ba("10000000")) == (8, ba())
    assert ic.codec.read_varnibble(ba("10000001")) == (9, ba())
    assert ic.codec.read_varnibble(ba("10000001110")) == (9, ba("110"))
    assert ic.codec.read_varnibble(ba("10111111")) == (71, ba())
    assert ic.codec.read_varnibble(ba("101111110")) == (71, ba("0"))
    assert ic.codec.read_varnibble(ba("110000000000")) == (72, ba())
    assert ic.codec.read_varnibble(ba("11000000000010")) == (72, ba("10"))
    assert ic.codec.read_varnibble(ba("110000000001")) == (73, ba())
    assert ic.codec.read_varnibble(ba("110000000001010")) == (73, ba("010"))
    assert ic.codec.read_varnibble(ba("110111111111")) == (583, ba())
    assert ic.codec.read_varnibble(ba("1101111111111010")) == (583, ba("1010"))
    assert ic.codec.read_varnibble(ba("1110000000000000")) == (584, ba())
    assert ic.codec.read_varnibble(ba("111000000000000001010")) == (
        584,
        ba("01010"),
    )
    assert ic.codec.read_varnibble(ba("1110111111111111")) == (4679, ba())
    assert ic.codec.read_varnibble(ba("1110111111111111101010")) == (
        4679,
        ba("101010"),
    )


def test_codec_clean():
    assert ic.codec.clean("somecode") == "somecode"
    assert ic.codec.clean("ISCC: SOME-CODE") == "SOMECODE"
    assert ic.codec.clean(" SOMECODE ") == "SOMECODE"
    assert ic.codec.clean("ISCC:") == ""


def test_codec_clean_raises_bad_scheme():
    with pytest.raises(ValueError):
        ic.clean("http://whatever")


def test_codec_clean_raises_multiple_colom():
    with pytest.raises(ValueError):
        ic.clean("ISCC:something:something")


def test_code_properties():
    c64 = ic.codec.Code(ic.gen_meta_code("Hello World").iscc)
    c256 = ic.codec.Code(ic.gen_meta_code("Hello World", bits=256).iscc)
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
    assert c64.maintype == ic.codec.MT.META
    assert c64.maintype == 0
    assert c64.subtype == ic.codec.ST.NONE
    assert c64.subtype == 0
    assert c64.version == ic.codec.VS.V0
    assert c64.length == 64
    assert c256.length == 256
    assert c64 ^ c64 == 0
    with pytest.raises(ValueError):
        _ = c64 ^ c256
    assert c64 == ic.codec.Code(c64.bytes)
    assert c64 == ic.codec.Code(c64.code)
    assert c64 == ic.codec.Code(tuple(c64))
    assert isinstance(c64.hash_ba, frozenbitarray)


def test_code_hashable():
    code = ic.codec.Code.rnd()
    assert code in {code}


def test_Code_uri():
    mco = ic.gen_meta_code("This is an URI representation of a Meta-Code")
    assert mco.code_obj.code == "AAARFRYHMQI6KPP6"
    assert mco.code_obj.uri == "iscc:aaarfryhmqi6kpp6"


def test_Code_mf_base16():
    mco = ic.gen_meta_code("Hello base16")
    assert mco.code_obj.code == "AAAWK77HZL7JPEN3"
    assert mco.code_obj.mf_base16 == "fcc010001657fe7cafe9791bb"
    assert ic.normalize("fcc010001657fe7cafe9791bb") == "ISCC:AAAWK77HZL7JPEN3"


def test_Code_mf_base32():
    mco = ic.gen_meta_code("Hello base32")
    assert mco.code_obj.code == "AAAW277H32PJOVML"
    assert mco.code_obj.mf_base32 == "bzqaqaalnp7t55huxkwfq"
    assert ic.normalize("bzqaqaalnp7t55huxkwfq") == "ISCC:AAAW277H32PJOVML"


def test_Code_mf_base58btc():
    mco = ic.gen_meta_code("Hello base58btc")
    assert mco.code_obj.code == "AAASO77HR4FFOEOK"
    assert mco.code_obj.mf_base58btc == "z4rHVQUUrBJhyW2Hqs"
    assert ic.normalize("z4rHVQUUrBJhyW2Hqs") == "ISCC:AAASO77HR4FFOEOK"


def test_Code_mf_base64url():
    mco = ic.gen_meta_code("This is a base64url encoded Meta-Code")
    assert mco.code_obj.code == "AAARQFT7MCK4LPO7"
    assert mco.code_obj.mf_base64url == "uzAEAARgWf2CVxb3f"
    assert ic.normalize("uzAEAARgWf2CVxb3f") == "ISCC:AAARQFT7MCK4LPO7"


def test_Code_raises():
    with pytest.raises(ValueError):
        ic.codec.Code(13)


def test_Code_Code():
    code = ic.codec.Code.rnd(ic.codec.MT.META)
    assert ic.codec.Code(code) == code


def test_Code_str_repr():
    mco = ic.gen_meta_code("Hello str")
    assert mco.code_obj.code == "AAAWOMHEVMWZ2EYF"
    assert str(mco.code_obj) == "AAAWOMHEVMWZ2EYF"
    assert repr(mco.code_obj) == 'Code("AAAWOMHEVMWZ2EYF")'
    assert (
        bytes(mco.code_obj).hex() == "00016730e4ab2d9d1305" == mco.code_obj.bytes.hex()
    )


def test_decompose_single_component():
    mts = (
        ic.MT.META,
        ic.MT.CONTENT,
        ic.MT.DATA,
        ic.MT.INSTANCE,
    )
    for mt in mts:
        code = ic.codec.Code.rnd(mt=mt)
        assert ic.codec.decompose(code.code)[0] == code.code


def test_decompose_data_instance():
    data = "GABTMCHNLCHTI2NHZFXOLEB53KSPU"
    inst = "IAB3GN6WUSNSX3MJBT6PBTVFAQZ7G"
    di = [data, inst]
    code = ic.iscc_code.gen_iscc_code_v0([data, inst]).iscc
    assert code == "KUDTMCHNLCHTI2NHZFXOLEB53KSPVMZX22SJWK7NREGPZ4GOUUCDH4Y"
    assert ic.decompose(code) == di


def test_decompose_content_data_instance():
    cont = "EMARIURG4CVZ3M7N"
    data = "GAA7ER72LMA6IOIO"
    inst = "IAAX3C2BUFV6XPQV"
    di = [cont, data, inst]
    code = ic.iscc_code.gen_iscc_code_v0([cont, data, inst]).iscc
    assert code == "KMCRIURG4CVZ3M7N6JD7UWYB4Q4Q47MLIGQWX256CU"
    assert ic.decompose(code) == di


def test_decompose_meta_content_data_instance():
    meta = "AAA4CPEJKZZ7A4HZ"
    cont = "EEAWM2CZ44CHDRHV"
    data = "GAA2F344YTSCRKBD"
    inst = "IAA4FWMY2ANPAYWJ"
    di = [meta, cont, data, inst]
    code = ic.iscc_code.gen_iscc_code_v0([meta, cont, data, inst]).iscc
    assert code == "KED4CPEJKZZ7A4HZMZUFTZYEOHCPLIXPTTCOIKFIEPBNTGGQDLYGFSI"
    assert ic.decompose(code) == di


def test_decompose_invalid():
    body = os.urandom(16)
    code = ic.encode_component(ic.MT.ISCC, ic.ST_ISCC.TEXT, 0, 128, body)
    with pytest.raises(ValueError):
        ic.decompose(code)


def test_decompose_str_of_codes():
    mco = ic.codec.Code.rnd(ic.codec.MT.META)
    cco = ic.codec.Code.rnd(ic.codec.MT.CONTENT)
    dco = ic.codec.Code.rnd(ic.codec.MT.DATA)
    ico = ic.codec.Code.rnd(ic.codec.MT.INSTANCE)
    iscc = f"ISCC:{mco.code}-{cco.code}-{dco.code}-{ico.code}"
    codes = ic.codec.decompose(iscc)
    assert codes == [mco.code, cco.code, dco.code, ico.code]


def test_Code_rnd():
    cco = ic.Code.rnd(mt=ic.MT.CONTENT, st=ic.ST_CC.TEXT)
    assert cco.maintype == ic.MT.CONTENT
    assert cco.subtype == ic.ST_CC.TEXT
    assert ic.Code.rnd(ic.MT.ISCC).maintype == ic.MT.ISCC
    assert ic.Code.rnd(ic.MT.ID).maintype == ic.MT.ID
    assert ic.Code.rnd(ic.MT.DATA).maintype == ic.MT.DATA


def test_normalize_single_canonical():
    n = ic.normalize("ISCC:AAATTZCKVH3S42TP")
    assert n == "ISCC:AAATTZCKVH3S42TP"


def test_normalize_single_no_scheme():
    n = ic.normalize("AAATTZCKVH3S42TP")
    assert n == "ISCC:AAATTZCKVH3S42TP"


def test_normalize_single_lower():
    n = ic.normalize("aaattzckvh3s42tp")
    assert n == "ISCC:AAATTZCKVH3S42TP"


def test_normalize_single_mixed_case():
    n = ic.normalize("AaAtTzckVh3s42tP")
    assert n == "ISCC:AAATTZCKVH3S42TP"


def test_normalize_dual():
    n = ic.normalize("GAAW2PRCRS5LNVZVIAAUVACQKXE3V44W")
    assert n == "ISCC:KUBW2PRCRS5LNVZVJKAFAVOJXLZZM"


def test_normalize_dual_dash():
    n = ic.normalize("GAAW2PRCRS5LNVZV-IAAUVACQKXE3V44W")
    assert n == "ISCC:KUBW2PRCRS5LNVZVJKAFAVOJXLZZM"


def test_clean_dual_dash():
    assert (
        ic.clean("GAAW2PRCRS5LNVZV-IAAUVACQKXE3V44W")
        == "GAAW2PRCRS5LNVZVIAAUVACQKXE3V44W"
    )


def test_normalize_dual_scheme():
    n = ic.normalize("ISCC:GAAW2PRCRS5LNVZVIAAUVACQKXE3V44W")
    assert n == "ISCC:KUBW2PRCRS5LNVZVJKAFAVOJXLZZM"


def test_normalize_dual_scheme_dash():
    n = ic.normalize("ISCC:GAAW2PRCRS5LNVZV-IAAUVACQKXE3V44W")
    assert n == "ISCC:KUBW2PRCRS5LNVZVJKAFAVOJXLZZM"


def test_normalize_triple():
    n = ic.normalize("EMAZQGH26X5XQ5HAGAA5U77EOAU2NU4YIAAU4SKRQCZZEYQD")
    assert n == "ISCC:KMCZQGH26X5XQ5HA3J76I4BJU3JZQTSJKGALHETCAM"


def test_normalize_triple_dash():
    n = ic.normalize("EMAZQGH26X5XQ5HA-GAA5U77EOAU2NU4Y-IAAU4SKRQCZZEYQD")
    assert n == "ISCC:KMCZQGH26X5XQ5HA3J76I4BJU3JZQTSJKGALHETCAM"


def test_normalize_triple_scheme():
    n = ic.normalize("ISCC:EMAZQGH26X5XQ5HAGAA5U77EOAU2NU4YIAAU4SKRQCZZEYQD")
    assert n == "ISCC:KMCZQGH26X5XQ5HA3J76I4BJU3JZQTSJKGALHETCAM"


def test_normalize_triple_scheme_dash():
    n = ic.normalize("ISCC:EMAZQGH26X5XQ5HA-GAA5U77EOAU2NU4Y-IAAU4SKRQCZZEYQD")
    assert n == "ISCC:KMCZQGH26X5XQ5HA3J76I4BJU3JZQTSJKGALHETCAM"


def test_normalize_full_scheme():
    n = ic.normalize("ISCC:KED4CPEJKZZ7A4HZMZUFTZYEOHCPLIXPTTCOIKFIEPBNTGGQDLYGFSI")
    assert n == "ISCC:KED4CPEJKZZ7A4HZMZUFTZYEOHCPLIXPTTCOIKFIEPBNTGGQDLYGFSI"


def test_normalize_full_scheme_lower():
    n = ic.normalize("iscc:ked4cpejkzz7a4hzmzuftzyeohcplixpttcoikfiepbntggqdlygfsi")
    assert n == "ISCC:KED4CPEJKZZ7A4HZMZUFTZYEOHCPLIXPTTCOIKFIEPBNTGGQDLYGFSI"


def test_normalize_full_no_scheme():
    n = ic.normalize("KED4CPEJKZZ7A4HZMZUFTZYEOHCPLIXPTTCOIKFIEPBNTGGQDLYGFSI")
    assert n == "ISCC:KED4CPEJKZZ7A4HZMZUFTZYEOHCPLIXPTTCOIKFIEPBNTGGQDLYGFSI"


def test_normalize_full_lower_no_scheme():
    n = ic.normalize("ked4cpejkzz7a4hzmzuftzyeohcplixpttcoikfiepbntggqdlygfsi")
    assert n == "ISCC:KED4CPEJKZZ7A4HZMZUFTZYEOHCPLIXPTTCOIKFIEPBNTGGQDLYGFSI"


def test_normalize_iscc_id():
    assert ic.normalize("MAAGZTFQTTVIZPJR") == "ISCC:MAAGZTFQTTVIZPJR"


def test_normalize_iscc_id_lower():
    assert ic.normalize("maagztfqttvizpjr") == "ISCC:MAAGZTFQTTVIZPJR"


def test_normalize_iscc_id_mixed():
    assert ic.normalize("MaaGZTfqttvizpjr") == "ISCC:MAAGZTFQTTVIZPJR"


def test_normalize_iscc_id_scheme():
    assert ic.normalize("ISCC:MAAGZTFQTTVIZPJR") == "ISCC:MAAGZTFQTTVIZPJR"


def test_normalize_iscc_id_scheme_lower():
    assert ic.normalize("iscc:maagztfqttvizpjr") == "ISCC:MAAGZTFQTTVIZPJR"


def test_normalize_iscc_id_scheme_mixed():
    assert ic.normalize("Iscc:Maagztfqttvizpjr") == "ISCC:MAAGZTFQTTVIZPJR"


def test_normalize_mf_base16_single():
    assert ic.normalize("fcc010001657fe7cafe9791bb") == "ISCC:AAAWK77HZL7JPEN3"


def test_normalize_mf_base32_single():
    assert ic.normalize("bzqaqaai35i25crx2mvpa") == "ISCC:AAARX2RV2FDPUZK6"


def test_normalize_mf_base58btc_single():
    assert ic.normalize("z4rHVQUUrBJhyW2Hqs") == "ISCC:AAASO77HR4FFOEOK"


def test_normalize_mf_base64_url_single():
    assert ic.normalize("uzAEAARvqNdFG-mVe") == "ISCC:AAARX2RV2FDPUZK6"


def test_codec_normalize_raises():
    code = ic.gen_meta_code("Hello", "World")
    bad = "f" + (b"\xcc\xff" + code.code_obj.bytes).hex()
    with pytest.raises(ValueError):
        ic.normalize(bad)
