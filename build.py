# -*- coding: utf-8 -*-
"""
Build cython extension modules.

The shared library can also be built manually using the command:
$ cythonize -X language_level=3 -a -i ./iscc_core/cdc.py
$ cythonize -X language_level=3 -a -i ./iscc_core/minhash.py
$ cythonize -X language_level=3 -a -i ./iscc_core/simhash.py
"""
try:
    from Cython.Build import cythonize, build_ext
    from distutils.core import Distribution
except ImportError:
    # dummy build function for poetry
    def build(setup_kwargs):
        return setup_kwargs

else:

    def build(setup_kwargs):
        extensions = cythonize(["iscc_core/cdc.py", "iscc_core/minhash.py", "iscc_core/simhash.py"])
        setup_kwargs.update(dict(ext_modules=extensions))
        return setup_kwargs
