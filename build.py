# -*- coding: utf-8 -*-
"""
Build cython extension modules.

The shared library can also be built manually using the command:
$ cythonize -X language_level=3 -a -i ./iscc_core/cdc.py
$ cythonize -X language_level=3 -a -i ./iscc_core/minhash.py
$ cythonize -X language_level=3 -a -i ./iscc_core/simhash.py
"""
from distutils.command.build_ext import build_ext
from distutils.core import Distribution


def build(setup_kwargs):
    try:
        from Cython.Build import cythonize
    except ImportError:
        print("WARNING: Cython not installed. Skipping extension build.")
        return setup_kwargs

    extensions = cythonize(["iscc_core/cdc.py", "iscc_core/minhash.py", "iscc_core/simhash.py"])
    distribution = Distribution({"name": "iscc_core", "ext_modules": extensions})
    distribution.package_dir = "iscc_core"
    try:
        cmd = build_ext(distribution)
        cmd.ensure_finalized()
        cmd.run()
    except Exception as e:
        print(e)
        print("********************************************************************")
        print("Failed to compile C accelerator module, falling back to pure python.")
        print("********************************************************************")
    return setup_kwargs
