"""Conditionally compile Cython extensions for binary wheel builds."""

import os
from setuptools import setup

ext_modules = []

if os.environ.get("CIBUILDWHEEL") == "1":
    from Cython.Build import cythonize

    ext_modules = cythonize(
        [
            "iscc_core/cdc.py",
            "iscc_core/minhash.py",
            "iscc_core/simhash.py",
            "iscc_core/dct.py",
            "iscc_core/wtahash.py",
        ],
        compiler_directives={"language_level": "3"},
    )

setup(ext_modules=ext_modules)
