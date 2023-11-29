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
except ImportError:
    def build(setup_kwargs):  # type: (dict) -> None
        pass

else:

    class build_ext_graceful(build_ext):
        """Custom build extension class with error propagation."""

        def run(self):
            """Compile C accelerator modules and propagate errors."""
            try:
                print("Trying to compile C accelerator modules")
                super().run()
                print("Successfully compiled C accelerator modules")
            except Exception as e:
                print(f"Error during compilation: {e}")
                raise  # Rethrow the exception to ensure it's captured by poetry

        def build_extensions(self):
            """Build extensions with error propagation."""
            try:
                print("Trying to compile C accelerator modules")
                super().build_extensions()
                print("Successfully compiled C accelerator modules")
            except Exception as e:
                print(f"Error during compilation: {e}")
                raise  # Rethrow the exception

    def build(setup_kwargs):  # type: (dict) -> None
        """Configure setup kwargs for Cython compilation with error propagation."""
        try:
            setup_kwargs.update(
                {
                    "ext_modules": cythonize(
                        [
                            "iscc_core/cdc.py",
                            "iscc_core/minhash.py",
                            "iscc_core/simhash.py",
                        ],
                        language_level="3",
                    ),
                    "cmdclass": {"build_ext": build_ext_graceful},
                }
            )
        except Exception as e:
            print(f"Error in setup configuration: {e}")
            raise  # Rethrow the exception
