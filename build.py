# -*- coding: utf-8 -*-
"""
The shared library can also be built manually using the command:
$ cythonize -X language_level=3 -a -i ./iscc_core/cdc.py
$ cythonize -X language_level=3 -a -i ./iscc_core/minhash.py
$ cythonize -X language_level=3 -a -i ./iscc_core/simhash.py
"""


def build(setup_kwargs):
    try:
        from Cython.Build import cythonize, build_ext

        setup_kwargs.update(
            dict(
                ext_modules=cythonize(
                    [
                        "iscc_core/cdc.py",
                        "iscc_core/minhash.py",
                        "iscc_core/simhash.py",
                    ]
                ),
                cmdclass=dict(build_ext=build_ext),
            )
        )
        print("************************************************************")
        print("Succeeded to compile Cython/C accelerator modules :)       *")
        print("************************************************************")
    except Exception as e:
        print("************************************************************")
        print("Cannot compile C accelerator module, use pure python version")
        print("************************************************************")
        print(e)
