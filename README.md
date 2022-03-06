# ISCC - Codec & Algorithms

[![Build](https://github.com/iscc/iscc-core/actions/workflows/tests.yml/badge.svg)](https://github.com/iscc/iscc-core/actions/workflows/tests.yml)
[![Version](https://img.shields.io/pypi/v/iscc-core.svg)](https://pypi.python.org/pypi/iscc-core/)
[![Coverage](https://codecov.io/gh/iscc/iscc-core/branch/main/graph/badge.svg?token=7BJ7HJU815)](https://codecov.io/gh/iscc/iscc-core)
[![Quality](https://app.codacy.com/project/badge/Grade/ad1cc48ac0c0413ea2373a938148f019)](https://www.codacy.com/gh/iscc/iscc-core/dashboard)
[![Downloads](https://pepy.tech/badge/iscc-core)](https://pepy.tech/project/iscc-core)

`iscc-core` is a Python library that implements the core algorithms of the [ISCC](https://core.iscc.codes) (*International Standard Content Code*)

## What is an ISCC

The ISCC is a similarity preserving identifier for digital media assets.

ISCCs are generated algorithmically from digital content, just like cryptographic hashes. However, instead of using a single cryptographic hash function to identify data only, the ISCC uses various algorithms to create a composite identifier that exhibits similarity-preserving properties (soft hash).

The component-based structure of the ISCC identifies content at multiple levels of abstraction. Each component is self-describing, modular, and can be used separately or with others to aid in various content identification tasks. The algorithmic design supports content deduplication, database synchronization, indexing, integrity verification, timestamping, versioning, data provenance, similarity clustering, anomaly detection, usage tracking, allocation of royalties, fact-checking and general digital asset management use-cases.

## What is `iscc-core`

`iscc-core` is the python based library of the core algorithms to create standard-compliant ISCC codes. It also serves as a reference for porting ISCC to other programming languages.

!!! tip
    This is a low level reference implementation. `iscc-core` does not support mediatype detection, metadata extraction or file format specific content extraction. For easy generation of ISCC codes see: [iscc-cli](https://github.com/iscc/iscc-cli/releases)

## ISCC Architecture

![ISCC Architecture](https://raw.githubusercontent.com/iscc/iscc-core/master/docs/images/iscc-codec-light.png)

## ISCC MainTypes

| Idx | Slug     | Bits | Purpose                                                  |
|-----|:---------|------|----------------------------------------------------------|
| 0   | META     | 0000 | Match on metadata similarity                             |
| 1   | SEMANTIC | 0001 | Match on semantic content similarity                     |
| 2   | CONTENT  | 0010 | Match on perceptual content similarity                   |
| 3   | DATA     | 0011 | Match on data similarity                                 |
| 4   | INSTANCE | 0100 | Match on data identity                                   |
| 5   | ISCC     | 0101 | Composite of two or more components with common header   |
| 6   | ID       | 0110 | Short unique identifier bound to ISCC, timestamp, pubkey |
| 7   | FLAKE    | 0111 | Unique time, randomness and counter based distributed ID |

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install `iscc-core`.

```bash
pip install iscc-core
```

## Quick Start

```python
import iscc_core as ic


meta_code = ic.gen_meta_code(name="ISCC Test Document!")

print(f"Meta-Code:     {meta_code['iscc']}")
print(f"Structure:     {ic.iscc_explain(meta_code['iscc'])}\n")

# Extract text from file
with open("demo.txt", "rt", encoding="utf-8") as stream:
    text = stream.read()
    text_code = ic.gen_text_code_v0(text)
    print(f"Text-Code:     {text_code['iscc']}")
    print(f"Structure:     {ic.iscc_explain(text_code['iscc'])}\n")

# Process raw bytes of textfile
with open("demo.txt", "rb") as stream:
    data_code = ic.gen_data_code(stream)
    print(f"Data-Code:     {data_code['iscc']}")
    print(f"Structure:     {ic.iscc_explain(data_code['iscc'])}\n")

    stream.seek(0)
    instance_code = ic.gen_instance_code(stream)
    print(f"Instance-Code: {instance_code['iscc']}")
    print(f"Structure:     {ic.iscc_explain(instance_code['iscc'])}\n")

iscc_code = ic.gen_iscc_code(
    (meta_code["iscc"], text_code["iscc"], data_code["iscc"], instance_code["iscc"])
)

iscc_obj = ic.Code(iscc_code["iscc"])
print(f"ISCC-CODE:     {iscc_obj.code}")
print(f"Structure:     {iscc_obj.explain}")
print(f"Multiformat:   {iscc_obj.mf_base32}\n")

iscc_id = ic.gen_iscc_id(iscc_obj.code, chain_id=1, wallet="1Bq568oLhi5HvdgC6rcBSGmu4G3FeAntCz")
iscc_id_obj = ic.Code(iscc_id["iscc"])
print(f"ISCC-ID:       {iscc_id_obj.code}")
print(f"Structure:     {iscc_id_obj.explain}")
print(f"Multiformat:   {iscc_id_obj.mf_base32}")
```

The output of this example is as follows:

```
Meta-Code:     ISCC:AAAT4EBWK27737D2
Structure:     META-NONE-V0-64-3e103656bffdfc7a

Text-Code:     ISCC:EAAQMBEYQF6457DP
Structure:     CONTENT-TEXT-V0-64-060498817dcefc6f

Data-Code:     ISCC:GAA7UJMLDXHPPENG
Structure:     DATA-NONE-V0-64-fa258b1dcef791a6

Instance-Code: ISCC:IAA3Y7HR2FEZCU4N
Structure:     INSTANCE-NONE-V0-64-bc7cf1d14991538d

ISCC-CODE:     KACT4EBWK27737D2AYCJRAL5Z36G76RFRMO4554RU26HZ4ORJGIVHDI
Structure:     ISCC-TEXT-V0-MCDI-3e103656bffdfc7a060498817dcefc6ffa258b1dcef791a6bc7cf1d14991538d
Multiformat:   bzqavabj6ca3fnp757r5ambeyqf6457dp7isywhoo66i2npd46hiutektru

ISCC-ID:       MEAJU5AXCPOIOYFL
Structure:     ID-BITCOIN-V0-64-9a741713dc8760ab
Multiformat:   bzqawcae2oqlrhxehmcvq
```

## Documentation

<https://core.iscc.codes>

## Project Status

The ISCC has been accepted by ISO as full work item ISO/AWI 24138 - International Standard Content
Code and is currently being standardized at TC 46/SC 9/WG 18. https://www.iso.org/standard/77899.html

!!! attention

    The iscc-core library and the accompanying documentation is under development. API changes and
    other backward incompatible changes are to be expected until the upcoming v1.5 stable release.


## Maintainers
[@titusz](https://github.com/titusz)

## Contributing

Pull requests are welcome. For significant changes, please open an issue first to discuss your plans. Please make sure to update tests as appropriate.

You may also want join our developer chat on Telegram at <https://t.me/iscc_dev>.

## Changelog

### 0.2.3 - 2022-03-06
- Update to iscc-schema 0.3.3
- Change image normalization instructions
- Fix issue with exporting cdc cython only functions

### 0.2.1 - 2022-03-03
- Cleanup and update dependencies
- Fix bitarray api change
- Fix developer commands

### 0.2.0 - 2022-02-24
- Complete API refactoring
- Use Data-URL as input for Meta-Code
- Use wallet address for ISCC-ID creation
- Added new Flake-Code (distributed time/random ID)
- Replaced assertions with exeptions
- Use secure random functions
- Retired Python 3.6 support (EOL)
- Return simple `dict` objects from generator functions
- Added ISCC string validation
- Added multiple helper functions

### 0.1.9 - 2021-12-17

- Added warning on non-standard options
- Added multiformats support
- Added uri representation
- Removed redundant cdc_avg_chunk_size option
- Updated codec format documentation

### 0.1.8 - 2021-12-12
- Added conformance tests for all top level functions
- Added conformance tests to source dir
- Added conformance module with `selftest` function
- Changed gen_image_code to accept normalized pixels instead of stream
- Changed opts to core_opts
- Removed image pre-processing and Pillow dependency
- Fixed readability of conformance tests
- Fixed soft_hash_video_v0 to accept non-tuple sequences
- Updated example code

### 0.1.7 - 2021-12-09
- Add dotenv for enviroment based configuration
- Cleanup package toplevel imports
- Return schema objects for iscc_code and iscc_id
- Exclude unset and none values from result dicts
- Add support for multiple code combinations for ISCC-CODE
- Add support for ISCC-ID based on singular Instance-Code
- Add initial conformance test system

### 0.1.6 - 2021-11-29
- Show counter for ISCC-ID in Code.explain

### 0.1.5 - 2021-11-28
- Fix documentation
- Change metahash creation logic
- Refactor models
- Add Content-Code-Mixed
- Add ISCC-ID
- Refactor `compose` to `gen_iscc_code`
- Refactor `models` to `schema`

### 0.1.4 - 2021-11-17
- Simplified options
- Optimize video WTA-hash for use with 64-bit granular features

### 0.1.3 - 2021-11-15
- Try to compile Cython/C accelerator modules when installing via pip
- Simplify soft_hash api return values
- Add .code() method to InstanceHasher, DataHasher
- Remove granular fingerprint calculation
- Add more top-level imports

### 0.1.2 - 2021-11-14
- Export more functions to toplevel
- Return schema driven objects from ISCC code generators.

### 0.1.1 - 2021-11-14
- Fix packaging problems

### 0.1.0 - 2021-11-13
- Initial release
