# ISCC - Codec & Algorithms

[![Build](https://github.com/iscc/iscc-core/actions/workflows/tests.yml/badge.svg)](https://github.com/iscc/iscc-core/actions/workflows/tests.yml)
[![Version](https://img.shields.io/pypi/v/iscc-core.svg)](https://pypi.python.org/pypi/iscc-core/)
[![Coverage](https://codecov.io/gh/iscc/iscc-core/branch/main/graph/badge.svg?token=7BJ7HJU815)](https://codecov.io/gh/iscc/iscc-core)
[![Quality](https://app.codacy.com/project/badge/Grade/ad1cc48ac0c0413ea2373a938148f019)](https://www.codacy.com/gh/iscc/iscc-core/dashboard)
[![Downloads](https://pepy.tech/badge/iscc-core)](https://pepy.tech/project/iscc-core)

`iscc-core` is the reference implementation of the core algorithms of the [ISCC](https://iscc.codes)
(*International Standard Content Code*)

## What is the ISCC

The ISCC is a similarity preserving fingerprint and identifier for digital media assets.

ISCCs are generated algorithmically from digital content, just like cryptographic hashes. However,
instead of using a single cryptographic hash function to identify data only, the ISCC uses various
algorithms to create a composite identifier that exhibits similarity-preserving properties (soft
hash).

The component-based structure of the ISCC identifies content at multiple levels of abstraction. Each
component is self-describing, modular, and can be used separately or with others to aid in various
content identification tasks. The algorithmic design supports content deduplication, database
synchronization, indexing, integrity verification, timestamping, versioning, data provenance,
similarity clustering, anomaly detection, usage tracking, allocation of royalties, fact-checking and
general digital asset management use-cases.

## What is `iscc-core`

`iscc-core` is a python based reference library of the core algorithms to create standard-compliant
ISCC codes. It also a good reference for porting ISCC to other programming languages.

!!! tip
    This is a low level reference implementation that does not inlcude features like mediatype
    detection, metadata extraction or file format specific content extraction. Please have a look at
    the [iscc-sdk](https://github.com/iscc/iscc-sdk) which adds those higher level features on top
    of the `iscc-core` library.

## ISCC Architecture

![ISCC Architecture](https://raw.githubusercontent.com/iscc/iscc-core/master/docs/images/iscc-codec-light.png#only-light)
![ISCC Architecture](https://raw.githubusercontent.com/iscc/iscc-core/master/docs/images/iscc-codec-dark.png#only-dark)

## ISCC MainTypes

| Idx | Slug     | Bits | Purpose                                                |
| --- | :------- | ---- | ------------------------------------------------------ |
| 0   | META     | 0000 | Match on metadata similarity                           |
| 1   | SEMANTIC | 0001 | Match on semantic content similarity                   |
| 2   | CONTENT  | 0010 | Match on perceptual content similarity                 |
| 3   | DATA     | 0011 | Match on data similarity                               |
| 4   | INSTANCE | 0100 | Match on data identity                                 |
| 5   | ISCC     | 0101 | Composite of two or more components with common header |

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install `iscc-core`.

```bash
pip install iscc-core
```

## Quick Start

```python
import json
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

# Combine ISCC-UNITs into ISCC-CODE
iscc_code = ic.gen_iscc_code(
    (meta_code["iscc"], text_code["iscc"], data_code["iscc"], instance_code["iscc"])
)

# Create convenience `Code` object from ISCC string
iscc_obj = ic.Code(iscc_code["iscc"])
print(f"ISCC-CODE:     {ic.iscc_normalize(iscc_obj.code)}")
print(f"Structure:     {iscc_obj.explain}")
print(f"Multiformat:   {iscc_obj.mf_base32}\n")

# Compare with changed ISCC-CODE:
new_dc, new_ic = ic.Code.rnd(mt=ic.MT.DATA), ic.Code.rnd(mt=ic.MT.INSTANCE)
new_iscc = ic.gen_iscc_code((meta_code["iscc"], text_code["iscc"], new_dc.uri, new_ic.uri))
print(f"Compare ISCC-CODES:\n{iscc_obj.uri}\n{new_iscc['iscc']}")
print(json.dumps(ic.iscc_compare(iscc_obj.code, new_iscc["iscc"]), indent=2))
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

ISCC-CODE:     ISCC:KACT4EBWK27737D2AYCJRAL5Z36G76RFRMO4554RU26HZ4ORJGIVHDI
Structure:     ISCC-TEXT-V0-MCDI-3e103656bffdfc7a060498817dcefc6ffa258b1dcef791a6bc7cf1d14991538d
Multiformat:   bzqavabj6ca3fnp757r5ambeyqf6457dp7isywhoo66i2npd46hiutektru

Compare ISCC-CODES:
ISCC:KACT4EBWK27737D2AYCJRAL5Z36G76RFRMO4554RU26HZ4ORJGIVHDI
ISCC:KACT4EBWK27737D2AYCJRAL5Z36G7Y7HA2BMECKMVRBEQXR2BJOS6NA
{
  "meta_dist": 0,
  "content_dist": 0,
  "data_dist": 33,
  "instance_match": false
}
```

## Documentation

<https://core.iscc.codes>

## Project Status

The ISCC has been accepted by ISO as full work item ISO/AWI 24138 - International Standard Content
Code and is currently being standardized at TC 46/SC 9/WG 18.
https://www.iso.org/standard/77899.html

!!! attention
    The iscc-core library and the accompanying documentation is under development. API changes and
    other backward incompatible changes are to be expected until the upcoming v1.5 stable release.

## Maintainers

[@titusz](https://github.com/titusz)

## Contributing

Pull requests are welcome. For significant changes, please open an issue first to discuss your
plans. Please make sure to update tests as appropriate.

You may also want join our developer chat on Telegram at <https://t.me/iscc_dev>.
