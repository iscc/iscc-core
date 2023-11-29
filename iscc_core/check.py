# -*- coding: utf-8 -*-
"""Inspect lib environment/installation"""
import inspect


__all__ = ["turbo"]


def turbo():
    # type: () -> bool
    """Check whether all optional cython extensions have been compiled to native modules."""
    from iscc_core import cdc, minhash, simhash

    modules = (cdc, minhash, simhash)
    for module in modules:
        module_file = inspect.getfile(module)
        if module_file.endswith(".py"):
            return False
    return True  # pragma: no cover
