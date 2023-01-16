# ISCC - Codec

This module implements encoding, decoding and transcoding functions of ISCC

## Codec Overview

![ISCC - data structure](../images/iscc-data-structure-light.svg#only-light)
![ISCC - data structure](../images/iscc-data-structure-dark.svg#only-dark)

## Codec Functions

::: iscc_core.codec
    options:
        show_source: true
        heading_level: 3
        members:
            - encode_component
            - encode_header
            - decode_header
            - encode_varnibble
            - decode_varnibble
            - encode_units
            - decode_units
            - encode_length
            - decode_length
            - encode_base32
            - decode_base32
            - iscc_decompose
            - iscc_normalize

## Alternate Encodings

::: iscc_core.codec
    options:
        show_source: true
        heading_level: 3
        members:
            - encode_base64
            - decode_base64
            - encode_base32hex
            - decode_base32hex


## Helper Functions

::: iscc_core.codec
    options:
        show_source: true
        heading_level: 3
        members:
            - iscc_decode
            - iscc_explain
            - iscc_type_id
            - iscc_validate
            - iscc_clean
