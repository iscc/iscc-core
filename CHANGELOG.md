# Changelog

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
