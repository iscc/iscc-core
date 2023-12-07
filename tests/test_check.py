# -*- coding: utf-8 -*-
import iscc_core as ic
import sys
import pytest


@pytest.mark.skipif(sys.version_info[:2] == (3, 12), reason="Needs investigation")
def test_check_turbo(turbo):
    if turbo is False:
        assert ic.turbo() is False
    else:
        assert ic.turbo() is True
