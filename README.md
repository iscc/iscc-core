# iscc-core - ISCC Core Algorithms

[![Build](https://github.com/iscc/iscc-core/actions/workflows/tests.yml/badge.svg)](https://github.com/iscc/iscc-core/actions/workflows/tests.yml)
[![Version](https://img.shields.io/pypi/v/iscc-core.svg)](https://pypi.python.org/pypi/iscc-core/)
[![Downloads](https://pepy.tech/badge/iscc-core)](https://pepy.tech/project/iscc-core)

> **iscc-core** is a Python library that implements the core algorithms of [ISCC v1.1](https://iscc.codes)
(International Standard Content Code)

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

image_path = "../docs/images/iscc-architecture.png"

meta_code = iscc_core.gen_meta_code(
    title="ISCC Architecure", extra="A schematic overview of the ISCC"
)

print(f"Meta-Code:     {meta_code.iscc}")
print(f"Structure:     {meta_code.code_obj.explain}\n")

with open(image_path, "rb") as stream:

    image_code = iscc_core.gen_image_code(stream)
    print(f"Image-Code:    {image_code.iscc}")
    print(f"Structure:     {image_code.code_obj.explain}\n")

    stream.seek(0)
    data_code = iscc_core.gen_data_code(stream)
    print(f"Data-Code:     {data_code.iscc}")
    print(f"Structure:     {data_code.code_obj.explain}\n")

    stream.seek(0)
    instance_code = iscc_core.gen_instance_code(stream)
    print(f"Instance-Code: {instance_code.iscc}")
    print(f"Structure:     {instance_code.code_obj.explain}\n")

iscc_code = iscc_core.gen_iscc_code(
    (meta_code.iscc, image_code.iscc, data_code.iscc, instance_code.iscc)
)
print(f"ISCC-CODE:     ISCC:{iscc_code.iscc}")
print(f"Structure:     {iscc_code.code_obj.explain}\n")

iscc_id = iscc_core.gen_iscc_id(chain=1, iscc_code=iscc_code.iscc, uc=7)
print(f"ISCC-ID:       ISCC:{iscc_id.iscc}")
print(f"Structure:     ISCC:{iscc_id.code_obj.explain}")
```

The output of this example is as follows:

```
Meta-Code:     AAA5H3V6SZHWDUKX
Structure:     META-NONE-V0-64-d3eebe964f61d157

Image-Code:    EEA6YTUFF6LJRWFG
Structure:     CONTENT-IMAGE-V0-64-ec4e852f9698d8a6

Data-Code:     GAAWYCDI6EHQFYBB
Structure:     DATA-NONE-V0-64-6c0868f10f02e021

Instance-Code: IAAQK76UVXOBJHJ3
Structure:     INSTANCE-NONE-V0-64-057fd4addc149d3b

ISCC-CODE:     ISCC:KED5H3V6SZHWDUKX5RHIKL4WTDMKM3AINDYQ6AXAEECX7VFN3QKJ2OY
Structure:     ISCC-IMAGE-V0-256-d3eebe964f61d157ec4e852f9698d8a66c0868f10f02e021057fd4addc149d3b

ISCC-ID:       ISCC:MEASB3COVS3Q6AGQA4
Structure:     ISCC:ID-BITCOIN-V0-72-20ec4eacb70f00d0-7
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


