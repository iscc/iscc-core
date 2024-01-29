# Changelog

## [1.0.8] - Unreleased
- Added implementors guide to README.md
- Improved pydantic v2 import logic
- Improved prefix extraction during normalization
- Improved canonical ISCC string validation

## [1.0.7] - 2024-01-07
- Support pydantic v1 & v2
- Updated dependencies

## [1.0.6] - 2023-12-15
- Added wheel package testing to CI
- Fixed incompatible dependencies

## [1.0.5] - 2023-12-07
- Improved simhash performance
- Added native dct and wtahash support
- Added Python 3.12 support
- Updated and relax dependencies

## [1.0.4] - 2023-06-05
- Removed bases dependency
- Fixed mkdocstrings
- Updated dependencies

## [1.0.3] - 2023-03-12
- Fix binary wheels

## [1.0.2] - 2023-03-12
- Publish binary wheels

## [1.0.1] - 2023-03-11
- Switch to standard bitarray module
- Switch tests to latest environments
- Add Python 3.11 support to TROVE classifiers

## [1.0.0] - 2023-01-24
- ISO/CD 24138 v1 Release
- Updateted dependencies

## [0.2.14] - 2023-01-17
- Added ISO Reference documentation
- Removed non-standard conformance tests
- Fixed Meta-Code documentation
- Improved documentation CSS

## [0.2.13] - 2023-01-16
- Added documentation for options
- Added python 3.11 support
- Added Markdown formating
- Added developmnet documentation
- Updated architecture figures
- Documentation cleanup
- Improved example code
- Optimized LF conversion
- Updated dependencies

## [0.2.12] - 2022-11-24
- Fixed issue with data url compound media types
- Added ISCC version validation to `iscc_validate`
- Added prefix check to `iscc_normalize`
- Bundled fonts with documentation
- Updated dependencies

## [0.2.11] - 2022-07-03
- Add support for gracefull build failures

## [0.2.10] - 2022-07-03
- Fix pip instalation is missing setuptools
- Update mkdocs

## [0.2.9] - 2022-07-03
- Added iscc_compare function
- Optimized soft_hash_audio performance
- Removed Cython from build requirements
- Fixed api listing tool
- Updated codec architecture figure
- Updated dependencies

## [0.2.8] - 2022-04-21
- Fixed bug with subtype for semantic code
- Changed URI representation to upper case
- Changed to disallow ISCC-ID creation from ISCC-IDs
- Added line conversion tool
- Removed source wheel distribution
- Updated dependencies

## [0.2.7] - 2022-04-16
- Fixed bug in iscc_id_incr_v0
- Added support to accept ISCC-ID URI as input for iscc_id_incr_v0
- Added guard against custom subtype in random ISCC-CODE generation.

## [0.2.6] - 2022-04-13
- Added `KY` and `MM` to valid prefixes
- Added support to check for compiled extension modules
- Added universal wheel distribution

## [0.2.5] - 2022-04-10
- Fixed missing `jcs` dependency
- Added SubType `NONE` to MT.ISCC to distinquish from SUM
- Added support for deterministic generation of random ISCC-CODEs
- Added support for custom bit-sizes for random ISCC-CODEs
- Moved changelog into separate file
- Updated dependencies

## [0.2.4] - 2022-03-19
- Updated dependencies
- Added Flake.from_int and Flake.from_string
- Made Flake comparable and hashable
- Use standard hex encoded multihash for datahash and metahash

## [0.2.3] - 2022-03-06
- Update to iscc-schema 0.3.3
- Change image normalization instructions
- Fix issue with exporting cdc cython only functions

## [0.2.1] - 2022-03-03
- Cleanup and update dependencies
- Fix bitarray api change
- Fix developer commands

## [0.2.0] - 2022-02-24
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

## [0.1.9] - 2021-12-17

- Added warning on non-standard options
- Added multiformats support
- Added uri representation
- Removed redundant cdc_avg_chunk_size option
- Updated codec format documentation

## [0.1.8] - 2021-12-12
- Added conformance tests for all top level functions
- Added conformance tests to source dir
- Added conformance module with `selftest` function
- Changed gen_image_code to accept normalized pixels instead of stream
- Changed opts to core_opts
- Removed image pre-processing and Pillow dependency
- Fixed readability of conformance tests
- Fixed soft_hash_video_v0 to accept non-tuple sequences
- Updated example code

## [0.1.7] - 2021-12-09
- Add dotenv for enviroment based configuration
- Cleanup package toplevel imports
- Return schema objects for iscc_code and iscc_id
- Exclude unset and none values from result dicts
- Add support for multiple code combinations for ISCC-CODE
- Add support for ISCC-ID based on singular Instance-Code
- Add initial conformance test system

## [0.1.6] - 2021-11-29
- Show counter for ISCC-ID in Code.explain

## [0.1.5] - 2021-11-28
- Fix documentation
- Change metahash creation logic
- Refactor models
- Add Content-Code-Mixed
- Add ISCC-ID
- Refactor `compose` to `gen_iscc_code`
- Refactor `models` to `schema`

## [0.1.4] - 2021-11-17
- Simplified options
- Optimize video WTA-hash for use with 64-bit granular features

## [0.1.3] - 2021-11-15
- Try to compile Cython/C accelerator modules when installing via pip
- Simplify soft_hash api return values
- Add .code() method to InstanceHasher, DataHasher
- Remove granular fingerprint calculation
- Add more top-level imports

## [0.1.2] - 2021-11-14
- Export more functions to toplevel
- Return schema driven objects from ISCC code generators.

## [0.1.1] - 2021-11-14
- Fix packaging problems

## [0.1.0] - 2021-11-13
- Initial release
