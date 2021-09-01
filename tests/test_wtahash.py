# -*- coding: utf-8 -*-
from iscc_core.wtahash import wtahash


def test_wtahash():
    vec = tuple([0] * 379) + (1,)
    assert (
        wtahash(vec).hex()
        == "0000000000000000000000000000000000000200000000000000000000000000"
    )
    vec = (1,) + tuple([0] * 379)
    assert (
        wtahash(vec).hex()
        == "0000000000000000000000000000000000000000000000000000000000000000"
    )
    vec = (1,) + tuple([0] * 378) + (1,)
    assert (
        wtahash(vec).hex()
        == "0000000000000000000000000000000000000200000000000000000000000000"
    )
    vec = (0,) + tuple([2] * 378) + (0,)
    assert (
        wtahash(vec).hex()
        == "0000000000000000000000000000000000000000000000000000000000000000"
    )
    vec = tuple(range(380))
    assert (
        wtahash(vec).hex()
        == "528f91431f7c4ad26932fc073a28cac93f21a3071a152fc2925bdaed1d190061"
    )
