# -*- coding: utf-8 -*-
import iscc_core


MID_64 = "AAAYPXW445FTYNJ3"
CID_64 = "EAARMJLTQCUWAND2"
DID_128 = "GABVVC5DMJJGYKZ4ZBYVNYABFFYXG"
IID_256 = "IADWIK7A7JTUAQ2D6QARX7OBEIK3OOUAM42LOBLCZ4ZOGDLRHMDL6TQ"

DID_64 = "GAAQQICFKJYKY4KU"


def test_gen_iscc_code_full():
    icode = iscc_core.gen_iscc_code([MID_64, CID_64, DID_128, IID_256])
    assert icode == {"iscc": "KADYPXW445FTYNJ3CYSXHAFJMA2HUWULUNRFE3BLHRSCXYH2M5AEGQY"}
    assert (
        icode.code_obj.explain
        == "ISCC-TEXT-V0-256-87dedce74b3c353b16257380a960347a5a8ba362526c2b3c642be0fa67404343"
    )


def test_gen_iscc_code_v0_full():
    icode = iscc_core.gen_iscc_code_v0([MID_64, CID_64, DID_128, IID_256])
    assert icode == {"iscc": "KADYPXW445FTYNJ3CYSXHAFJMA2HUWULUNRFE3BLHRSCXYH2M5AEGQY"}
    assert (
        icode.code_obj.explain
        == "ISCC-TEXT-V0-256-87dedce74b3c353b16257380a960347a5a8ba362526c2b3c642be0fa67404343"
    )


def test_gen_iscc_code_v0_no_meta():
    icode = iscc_core.gen_iscc_code_v0([CID_64, DID_128, IID_256])
    assert icode == {"iscc": "KACRMJLTQCUWAND2LKF2GYSSNQVTYZBL4D5GOQCDIM"}
    assert (
        icode.code_obj.explain
        == "ISCC-TEXT-V0-192-16257380a960347a5a8ba362526c2b3c642be0fa67404343"
    )


def test_gen_iscc_code_v0_no_meta_content_256():
    icode = iscc_core.gen_iscc_code_v0([DID_128, IID_256])
    assert icode == {"iscc": "KUDVVC5DMJJGYKZ4ZBYVNYABFFYXGZBL4D5GOQCDIP2ACG75YERBLNY"}
    assert (
        icode.code_obj.explain
        == "ISCC-SUM-V0-256-5a8ba362526c2b3cc87156e001297173642be0fa67404343f4011bfdc12215b7"
    )


def test_gen_iscc_code_v0_no_meta_content_128():
    icode = iscc_core.gen_iscc_code_v0([DID_64, IID_256])
    assert icode == {"iscc": "KUBQQICFKJYKY4KUMQV6B6THIBBUG"}
    assert icode.code_obj.explain == "ISCC-SUM-V0-128-0820455270ac7154642be0fa67404343"


def test_gen_iscc_code_v0_ordering():
    icode = iscc_core.gen_iscc_code_v0([CID_64, MID_64, IID_256, DID_128])
    assert icode == {"iscc": "KADYPXW445FTYNJ3CYSXHAFJMA2HUWULUNRFE3BLHRSCXYH2M5AEGQY"}
    assert (
        icode.code_obj.explain
        == "ISCC-TEXT-V0-256-87dedce74b3c353b16257380a960347a5a8ba362526c2b3c642be0fa67404343"
    )
