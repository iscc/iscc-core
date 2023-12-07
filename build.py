# -*- coding: utf-8 -*-
"""
Build cython extension modules.

The shared library can also be built manually using the command:
$ cythonize -X language_level=3 -a -i ./iscc_core/cdc.py
$ cythonize -X language_level=3 -a -i ./iscc_core/minhash.py
$ cythonize -X language_level=3 -a -i ./iscc_core/simhash.py
$ cythonize -X language_level=3 -a -i ./iscc_core/dct.py
$ cythonize -X language_level=3 -a -i ./iscc_core/wtahash.py
"""
try:
    from Cython.Build import cythonize, build_ext
except ImportError:
    # dummy build function for poetry
    def build(setup_kwargs):
        pass

else:

    class build_ext_gracefull(build_ext):
        def run(self):
            try:
                print("Trying to compile C accelerator modules")
                super().run()
                print("Successfully comiled C accelerator modules")
            except Exception as e:
                print(e)
                print("********************************************************************")
                print("Failed to compile C accelerator module, falling back to pure python.")
                print("********************************************************************")

        def build_extensions(self):
            try:
                print("Trying to compile C accelerator modules")
                super().build_extensions()
                print("Successfully comiled C accelerator modules")
            except Exception as e:
                print(e)
                print("********************************************************************")
                print("Failed to compile C accelerator module, falling back to pure python.")
                print("********************************************************************")

    def build(setup_kwargs):
        try:
            setup_kwargs.update(
                dict(
                    ext_modules=cythonize(
                        [
                            "iscc_core/cdc.py",
                            "iscc_core/minhash.py",
                            "iscc_core/simhash.py",
                            "iscc_core/dct.py",
                            "iscc_core/wtahash.py",
                        ]
                    ),
                    cmdclass=dict(build_ext=build_ext_gracefull),
                )
            )
        except Exception as e:
            print(e)
            print("********************************************************************")
            print("Failed to compile C accelerator module, falling back to pure python.")
            print("********************************************************************")
