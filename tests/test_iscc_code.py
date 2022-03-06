# -*- coding: utf-8 -*-
import pytest
from iscc_schema import IsccMeta
import iscc_core as ic


MID_64 = "AAAYPXW445FTYNJ3"
CID_64 = "EAARMJLTQCUWAND2"
DID_128 = "GABVVC5DMJJGYKZ4ZBYVNYABFFYXG"
IID_256 = "IADWIK7A7JTUAQ2D6QARX7OBEIK3OOUAM42LOBLCZ4ZOGDLRHMDL6TQ"

DID_64 = "GAAQQICFKJYKY4KU"


def test_gen_iscc_code_full():
    icode = ic.gen_iscc_code([MID_64, CID_64, DID_128, IID_256])
    assert icode == {"iscc": "ISCC:KACYPXW445FTYNJ3CYSXHAFJMA2HUWULUNRFE3BLHRSCXYH2M5AEGQY"}
    assert (
        ic.iscc_explain(icode["iscc"])
        == "ISCC-TEXT-V0-MCDI-87dedce74b3c353b16257380a960347a5a8ba362526c2b3c642be0fa67404343"
    )


def test_gen_iscc_code_v0_full():
    icode = ic.gen_iscc_code_v0([MID_64, CID_64, DID_128, IID_256])
    assert icode == {"iscc": "ISCC:KACYPXW445FTYNJ3CYSXHAFJMA2HUWULUNRFE3BLHRSCXYH2M5AEGQY"}
    assert (
        ic.iscc_explain(icode["iscc"])
        == "ISCC-TEXT-V0-MCDI-87dedce74b3c353b16257380a960347a5a8ba362526c2b3c642be0fa67404343"
    )


def test_gen_iscc_code_v0_no_meta():
    icode = ic.gen_iscc_code_v0([CID_64, DID_128, IID_256])
    assert icode == {"iscc": "ISCC:KAARMJLTQCUWAND2LKF2GYSSNQVTYZBL4D5GOQCDIM"}
    assert (
        ic.iscc_explain(icode["iscc"])
        == "ISCC-TEXT-V0-CDI-16257380a960347a5a8ba362526c2b3c642be0fa67404343"
    )


def test_gen_iscc_code_v0_no_meta_content():
    icode = ic.gen_iscc_code_v0([DID_128, IID_256])
    assert icode == {"iscc": "ISCC:KUAFVC5DMJJGYKZ4MQV6B6THIBBUG"}
    # TODO mabye show length for SubType SUM as we now the unit composition.
    # we may also get a ISCC-SUM-V0-256 version
    assert ic.iscc_explain(icode["iscc"]) == "ISCC-SUM-V0-DI-5a8ba362526c2b3c642be0fa67404343"


def test_gen_iscc_code_v0_no_meta_content_128():
    icode = ic.gen_iscc_code_v0([DID_64, IID_256])
    assert icode == {"iscc": "ISCC:KUAAQICFKJYKY4KUMQV6B6THIBBUG"}
    assert ic.iscc_explain(icode["iscc"]) == "ISCC-SUM-V0-DI-0820455270ac7154642be0fa67404343"
    assert IsccMeta(**icode).iscc == "ISCC:KUAAQICFKJYKY4KUMQV6B6THIBBUG"


def test_gen_iscc_code_v0_ordering():
    icode = ic.gen_iscc_code_v0([CID_64, MID_64, IID_256, DID_128])
    assert icode == {"iscc": "ISCC:KACYPXW445FTYNJ3CYSXHAFJMA2HUWULUNRFE3BLHRSCXYH2M5AEGQY"}
    assert (
        ic.iscc_explain(icode["iscc"])
        == "ISCC-TEXT-V0-MCDI-87dedce74b3c353b16257380a960347a5a8ba362526c2b3c642be0fa67404343"
    )
    assert IsccMeta(**icode).iscc == "ISCC:KACYPXW445FTYNJ3CYSXHAFJMA2HUWULUNRFE3BLHRSCXYH2M5AEGQY"


def test_gen_iscc_code_v0_insufficient_codes_raises():
    with pytest.raises(ValueError) as e:
        ic.gen_iscc_code_v0([CID_64])
        assert "Minimum two" in str(e)


def test_gen_iscc_code_v0_32_bit_codes_raise():
    with pytest.raises(ValueError) as e:
        ic.gen_iscc_code_v0(["AAAGKLHFXM", "EAAP5Q74YU"])
        assert "Cannot build" in str(e)


def test_gen_iscc_code_v0_data_or_instance_missing_raises():
    with pytest.raises(ValueError) as e:
        ic.gen_iscc_code_v0([MID_64, CID_64, DID_128])
        assert "ISCC-CODE requires" in str(e)


def test_gen_iscc_code_v0_incompat_semantic_content_raises():
    sema = ic.Code.rnd(ic.MT.SEMANTIC, 0, bits=64).code
    cont = ic.Code.rnd(ic.MT.CONTENT, 1, bits=64).code
    with pytest.raises(ValueError) as e:
        ic.gen_iscc_code_v0([sema, cont, DID_64, IID_256])
        assert "Semantic-Code" in str(e)
