# Coding Convetions

- Write pragmatic, easily testable, and performant code!
- Prefer short and pure functions where possible!
- Keep the number of function arguments as low as possible!
- Don´t use nested functions!
- Write concise and to-the-point docstrings for all functions!
- Use type comments style (PEP 484) instead of function annotations!
- Always add a correct PEP 484 style type comment as the first line after the function definition!
- Use built-in collection types as generic types for annotations (PEP 585)!
- Use the | (pipe) operator for writing union types (PEP 604)!

Example function with type annotations and docstring:

```python
def tokenize_chunks(chunks, max_len=None):
    # type: (list[str], int|None) -> dict
    """
    Tokenize text chunks into model-compatible formats.

    :param chunks: Text chunks to tokenize.
    :param max_len: Truncates chunks above max_len characters
    :return: Dictionary of tokenized data including input IDs, attention masks, and type IDs.
    """
```

This repository is the normative reference implementation for ISO 24138:2024.
All code edits must be made with the utmost care and attention to detail and with backwards
compatibility in mind. Implementation correctness and performance are crucial.

When making changes to `cdc.pyx` you must run `cythonize ./iscc_core/cdc.pyx` before benchmarking
the new implementation with `python -m benchmark.bench_code_data`. You may also experiment
with cythonize options to improve performance.

usage: cythonize [-h] [-X NAME=VALUE,...] [-E NAME=VALUE,...] [-s NAME=VALUE] [-2] [-3] [--3str] [-+] [-a] [--annotate-fullc] [-x PATTERN] [-b] [-i] [-j N] [-f] [-q] [--lenient] [-k] [--no-docstrings] [-M] [sources ...]

positional arguments:
  sources

options:
  -h, --help            show this help message and exit
  -X NAME=VALUE,..., --directive NAME=VALUE,...
                        set a compiler directive
  -E NAME=VALUE,..., --compile-time-env NAME=VALUE,...
                        set a compile time environment variable
  -s NAME=VALUE, --option NAME=VALUE
                        set a cythonize option
  -2                    use Python 2 syntax mode by default
  -3                    use Python 3 syntax mode by default
  --3str                use Python 3 syntax mode by default
  -+, --cplus           Compile as C++ rather than C
  -a, --annotate        Produce a colorized HTML version of the source.
  --annotate-fullc      Produce a colorized HTML version of the source which includes entire generated C/C++-code.
  -x PATTERN, --exclude PATTERN
                        exclude certain file patterns from the compilation
  -b, --build           build extension modules using distutils/setuptools
  -i, --inplace         build extension modules in place using distutils/setuptools (implies -b)
  -j N, --parallel N    run builds in N parallel jobs (default: 12)
  -f, --force           force recompilation
  -q, --quiet           be less verbose during compilation
  --lenient             increase Python compatibility by ignoring some compile time errors
  -k, --keep-going      compile as much as possible, ignore compilation failures
  --no-docstrings       strip docstrings
  -M, --depfile         produce depfiles for the sources

Environment variables:
  CYTHON_FORCE_REGEN: if set to 1, forces cythonize to regenerate the output files regardless
        of modification times and changes.
  Environment variables accepted by setuptools are supported to configure the C compiler and build:
  https://setuptools.pypa.io/en/latest/userguide/ext_modules.html#compiler-and-linker-options

