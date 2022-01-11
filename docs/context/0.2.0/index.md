---
hide:
  - navigation
---

# ISCC - Metadata Vocabulary (v0.2.0)

## @context

!!! term ""
    JSON-LD Context URI

## type

!!! term ""
    JSON Schema URI

## iscc

!!! term ""
    ISCC in canonical encoding.

## name

!!! term ""
    The name or title of the intangible creation manifested by the identified digital asset

## description

!!! term ""
    Description of the digital asset identified by the ISCC (used as input for Meta-Code generation). Any user presentable text string (including Markdown text) indicative of the identity of the referent may be used.

## image

!!! term ""
    URI for a user presentable image that serves as a preview of identified digital content or, in case of an NFT, the digital content itself.

## keywords

!!! term ""
    List of keywords relevant to the identified digital content.

## identifier

!!! term ""
    Other identifier(s) such as those defined by ISO/TC 46/SC 9 referencing the work, product or other abstraction of which the referenced digital asset is a full or partial manifestation.

## filename

!!! term ""
    Filename of the referenced digital asset (automatically used as fallback if no seed_title element is specified)

## filesize

!!! term ""
    File size of media asset in bytes.

## mediatype

!!! term ""
    IANA Media Type (MIME type)

## tophash

!!! term ""
    Multihash hash over concatenation of metahash and datahash

## metahash

!!! term ""
    Multihash hash of metadata.

## datahash

!!! term ""
    Multihash hash of media file.

## duration

!!! term ""
    Duration of audio-visual media in secondes.

## fps

!!! term ""
    Frames per second of video assets.

## width

!!! term ""
    Width of visual media in pixels.

## height

!!! term ""
    Height of visual media in pixels.

## characters

!!! term ""
    Number of text characters (code points after Unicode normalization)

## language

!!! term ""
    Language(s) of content (BCP-47) in weighted order.

## parts

!!! term ""
    Included Content-Codes.

## license

!!! term ""
    URI of license for the identified digital content.

## redirect

!!! term ""
    URL to which a resolver should redirect an ISCC-ID that has been minted from a declartion that includes the IPFS-hash of this metadata instance.

