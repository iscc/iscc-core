# -*- coding: utf-8 -*-
from iscc_core import check
import iscc_core as ic
import array


def test_check_suffix():
    assert check.suffix("hello.world") == "world"


def test_check_isnativemodule():
    assert check.isnativemodule(check) is False
    assert check.isnativemodule(array) is True


def test_check_turbo(turbo):
    if turbo is False:
        assert ic.turbo() is False
    else:
        assert ic.turbo() is True
