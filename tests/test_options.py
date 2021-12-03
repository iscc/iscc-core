# -*- coding: utf-8 -*-
import os
import pytest
from iscc_core.options import CoreOptions


def test_CoreOptions():
    assert CoreOptions().mixed_bits == 64


@pytest.fixture(scope="function")
def test_options_env_vars():

    # ENV Variables must be set before import of iscc_core package
    os.environ["META_BITS"] = "128"
    import iscc_core

    assert (
        iscc_core.gen_meta_code_v0("Hello World").code
        == "AAB77PPFVS6JDUQBWZDBIUGOUNAGI"
    )
