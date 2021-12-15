# -*- coding: utf-8 -*-
import os

# ENV Variables must be set before import of iscc_core package
os.environ["ISCC_CORE_META_TRIM_TITLE"] = "666"


def test_options_nonstandard():
    import iscc_core

    assert iscc_core.core_opts.meta_trim_title == 666
    assert iscc_core.options_conformant is False
    iscc_core.core_opts.meta_trim_title = 128


def test_options():
    import iscc_core

    assert iscc_core.core_opts.mixed_bits == 64
