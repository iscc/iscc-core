# -*- coding: utf-8 -*-
"""Inspect lib environment/installation"""
import inspect
from loguru import logger as log


__all__ = ["turbo"]


def turbo():  # pragma: no cover
    # type: () -> bool
    """Check whether all optional cython extensions have been compiled to native modules."""
    from iscc_core import cdc, minhash, simhash, dct, wtahash

    modules = (cdc, minhash, simhash, dct, wtahash)
    for module in modules:
        module_file = inspect.getfile(module)
        log.debug(f"Module {module.__name__} file: {module_file}")
        if module_file.endswith(".py"):
            return False
    return True
