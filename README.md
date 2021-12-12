# iscc-core - ISCC Core Algorithms

[![Build](https://github.com/iscc/iscc-core/actions/workflows/tests.yml/badge.svg)](https://github.com/iscc/iscc-core/actions/workflows/tests.yml)
[![Version](https://img.shields.io/pypi/v/iscc-core.svg)](https://pypi.python.org/pypi/iscc-core/)
[![Downloads](https://pepy.tech/badge/iscc-core)](https://pepy.tech/project/iscc-core)

> `iscc-core` is a Python library that implements the core algorithms of the [ISCC](https://iscc.codes)
(International Standard Content Code)

| NOTE: This is a low level reference implementation. `iscc-core` does not support content/metadata detection, extraction or preprocessing. For easy generation of ISCC codes see: [iscc-cli](https://github.com/iscc/iscc-cli) |
|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|

## What is ISCC

The **ISCC** (*International Standard Content Code*) is an identifier for digital media
assets.

An **ISCC** is derived algorithmically from the digital content itself, just like
cryptographic hashes. However, instead of using a single cryptographic hash function to
identify data only, the ISCC uses a variety of algorithms to create a composite
identifier that exhibits similarity-preserving properties (soft hash).

The component-based structure of the ISCC identifies content at multiple levels of
abstraction. Each component is self-describing, modular and can be used separately or
in conjunction with others to aid in various content identification tasks.

The algorithmic design supports scenarios that require content deduplication, database
synchronisation and indexing, integrity verification, timestamping, versioning, data
provenance, similarity clustering, anomaly detection, usage tracking, allocation of
royalties, fact-checking and general digital asset management use-cases.

## What is `iscc-core`

`iscc-core` is the python based library of the core algorithms to create standard
compliant **ISCC** codes. It also serves as a reference for porting ISCC to other
programming languages.

## ISCC Architecture

![ISCC Architecure](https://raw.githubusercontent.com/iscc/iscc-core/master/docs/images/iscc-architecture.png)

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install `iscc-core`.

```bash
pip install iscc-core
```

## Quick Start

```python
import iscc_core


meta_code = iscc_core.gen_meta_code(title="ISCC Test Document!")

print(f"Meta-Code:     ISCC:{meta_code.iscc}")
print(f"Structure:     {meta_code.code_obj.explain}\n")

# Extract text from file
with open('demo.txt', "rt", encoding='utf-8') as stream:
    text = stream.read()
    text_code = iscc_core.gen_text_code_v0(text)
    print(f"Text-Code:     ISCC:{text_code.iscc}")
    print(f"Structure:     {text_code.code_obj.explain}\n")

# Process raw bytes of textfile
with open('demo.txt', "rb") as stream:
    data_code = iscc_core.gen_data_code(stream)
    print(f"Data-Code:     ISCC:{data_code.iscc}")
    print(f"Structure:     {data_code.code_obj.explain}\n")

    stream.seek(0)
    instance_code = iscc_core.gen_instance_code(stream)
    print(f"Instance-Code: ISCC:{instance_code.iscc}")
    print(f"Structure:     {instance_code.code_obj.explain}\n")

iscc_code = iscc_core.gen_iscc_code(
    (meta_code.iscc, text_code.iscc, data_code.iscc, instance_code.iscc)
)
print(f"ISCC-CODE:     ISCC:{iscc_code.iscc}")
print(f"Structure:     {iscc_code.code_obj.explain}\n")

iscc_id = iscc_core.gen_iscc_id(chain=1, iscc_code=iscc_code.iscc, uc=7)
print(f"ISCC-ID:       ISCC:{iscc_id.iscc}")
print(f"Structure:     ISCC:{iscc_id.code_obj.explain}")

```

The output of this example is as follows:

```
Meta-Code:     ISCC:AAA3MGR7CSJ3O3D3
Structure:     META-NONE-V0-64-b61a3f1493b76c7b

Text-Code:     ISCC:EAASS2POFOWX6KDJ
Structure:     CONTENT-TEXT-V0-64-2969ee2bad7f2869

Data-Code:     ISCC:GAAZ5SQ47ZQ34A3V
Structure:     DATA-NONE-V0-64-9eca1cfe61be0375

Instance-Code: ISCC:IAASQF7FY2TLVFRC
Structure:     INSTANCE-NONE-V0-64-2817e5c6a6ba9622

ISCC-CODE:     ISCC:KAD3MGR7CSJ3O3D3FFU64K5NP4UGTHWKDT7GDPQDOUUBPZOGU25JMIQ
Structure:     ISCC-TEXT-V0-256-b61a3f1493b76c7b2969ee2bad7f28699eca1cfe61be03752817e5c6a6ba9622

ISCC-ID:       ISCC:MEASBPSKHY7KDPZIA4
Structure:     ISCC:ID-BITCOIN-V0-72-20be4a3e3ea1bf28-7
```

## Documentation

https://iscc-core.iscc.codes

## Project Status

ISCC is in the process of being standardized within
[ISO/TC 46/SC 9](https://www.iso.org/standard/77899.html).

## Maintainers
[@titusz](https://github.com/titusz)

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss
what you would like to change. Please make sure to update tests as appropriate.

You may also want join our developer chat on Telegram at <https://t.me/iscc_dev>.

## Changelog

### [0.1.8] - 2021-12-12
- Added conformance tests for all top level functions
- Added conformance tests to source dir
- Added conformance module with `selftest` function
- Changed gen_image_code to accept normalized pixels instead of stream
- Changed opts to core_opts
- Removed image pre-processing and Pillow dependency
- Fixed readability of conformance tests
- Fixed soft_hash_video_v0 to accept non-tuple sequences
- Updated example code

### [0.1.7] - 2021-12-09

- Add dotenv for enviroment based configuration
- Cleanup package toplevel imports
- Return schema objects for iscc_code and iscc_id
- Exclude unset and none values from result dicts
- Add support for multiple code combinations for ISCC-CODE
- Add support for ISCC-ID based on singular Instance-Code
- Add initial conformance test system

### [0.1.6] - 2021-11-29
- Show counter for ISCC-ID in Code.explain

### [0.1.5] - 2021-11-28

- Fix documentation
- Change metahash creation logic
- Refactor models
- Add Content-Code-Mixed
- Add ISCC-ID
- Refactor `compose` to `gen_iscc_code`
- Refactor `models` to `schema`

### [0.1.4] - 2021-11-17
- Simplified options
- Optimize video WTA-hash for use with 64-bit granular features

### [0.1.3] - 2021-11-15
- Try to compile Cython/C accelerator modules when installing via pip
- Simplify soft_hash api return values
- Add .code() method to InstanceHasher, DataHasher
- Remove granular fingerprint calculation
- Add more top-level imports

### [0.1.2] - 2021-11-14
- Export more functions to toplevel
- Return schema driven objects from ISCC code generators.

### [0.1.1] - 2021-11-14
- Fix packaging problems

### [0.1.0] - 2021-11-13
- Initial release


