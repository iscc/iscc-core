# -*- coding: utf-8 -*-
import iscc_core as ic


def test_check_turbo(turbo):
    if turbo is False:
        assert ic.turbo() is False
    else:
        assert ic.turbo() is True
