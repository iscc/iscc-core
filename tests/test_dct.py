# -*- coding: utf-8 -*-
import pytest
from iscc_core.dct import dct


def test_dct_empty():
    with pytest.raises(ValueError):
        dct([])


def test_dct_zeros():
    assert dct([0] * 64) == [0] * 64


def test_dct_ones():
    assert dct([1] * 64) == [64] + [0] * 63


def test_dct_range():
    assert dct(range(64))[0] == 2016
