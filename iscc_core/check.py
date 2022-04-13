# -*- coding: utf-8 -*-
"""Inspect lib environment/installation"""
import importlib.machinery
import inspect


EXTENSION_SUFFIXES = tuple(sf.lstrip(".") for sf in importlib.machinery.EXTENSION_SUFFIXES)


def suffix(filename):
    return "." in filename and filename.rpartition(".")[-1] or ""


def isnativemodule(module):
    """isnativemodule(thing) → boolean predicate, True if `module`
    is a native-compiled (“extension”) module.

    Q.v. this fine StackOverflow answer on this subject:
        https://stackoverflow.com/a/39304199/298171
    """
    # Step one: modules only beyond this point:
    if not inspect.ismodule(module):  # pragma: no cover
        return False

    # Step two: return truly when “__loader__” is set:
    if isinstance(
        getattr(module, "__loader__", None), importlib.machinery.ExtensionFileLoader
    ):  # pragma: no cover
        return True

    # Step three: in leu of either of those indicators,
    # check the module path’s file suffix:
    try:
        ext = suffix(inspect.getfile(module))
    except TypeError as exc:
        return "is a built-in" in str(exc)

    return ext in EXTENSION_SUFFIXES
