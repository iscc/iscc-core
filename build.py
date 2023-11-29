# -*- coding: utf-8 -*-
"""
Build cython extension modules.

The shared library can also be built manually using the command:
$ cythonize -X language_level=3 -a -i ./iscc_core/cdc.py
$ cythonize -X language_level=3 -a -i ./iscc_core/minhash.py
$ cythonize -X language_level=3 -a -i ./iscc_core/simhash.py
"""


def build(setup_kwargs):
    # Check if Cython is available
    try:
        from Cython.Build import cythonize
    except ImportError:
        print("Cython is not enabled, skipping build.")
        return

    try:
        setup_kwargs.update(
            {
                "ext_modules": cythonize(
                    [
                        "iscc_core/cdc.py",
                        "iscc_core/minhash.py",
                        "iscc_core/simhash.py",
                    ]
                ),
            }
        )
    except Exception as e:
        print(f"Warning: Cython build failed ({e}), using pure Python mode.")
