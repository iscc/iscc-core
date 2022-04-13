# -*- coding: utf-8 -*-
from iscc_core import cdc, minhash, simhash
from iscc_core import check
import array


def test_check_suffix():
    assert check.suffix("hello.world") == "world"


def test_check_isnativemodule():
    assert check.isnativemodule(check) is False
    assert check.isnativemodule(array) is True


def test_check_turbo(turbo):
    if turbo is False:
        assert check.isnativemodule(cdc) is False
        assert check.isnativemodule(simhash) is False
        assert check.isnativemodule(minhash) is False
    else:
        assert check.isnativemodule(cdc) is True
        assert check.isnativemodule(simhash) is True
        assert check.isnativemodule(minhash) is True
