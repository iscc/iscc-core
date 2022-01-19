# -*- coding: utf-8 -*-
"""*A similarity preserving hash for digital asset metadata*.

The Meta-Code is the first unit of a canonical ISCC. It is calculated from the metadata of a
digital asset. The purpose of the Meta-Code is to aid the discovery of digital assets with similar
metadata and the detection of metadata anomalies.

Because of its special role we call the metadata supplied to the algorithm SEED-METADATA.
SEED-METADATA has 3 possible inputs:

- **name** (required): The name or title of the work manifested by the digital asset.
- **description** (optional): A user-presentable textual description of the digital asset.
- **properties** (optional): Industry-sector or use-case specific structured metadata or a raw file
   header (binary blob).

The first 32-bits of a Meta-Code are calculated as a simliarity hash from the `name` field.
The second 32-bits are also calculated from the `name` field if no other input was supplied.
If a `description` is suplied but no `properties`, the description will be used for the second
32-bits. If `properties` are supplied it will be used in favour of `description` for the second
32-bits.

Due to the broad applicability of the ISCC we do not prescribe a particular schema for the metadata
supplied to the `properties`-field. However, structured metadata should be supplied as an object
that is JSON/JCS serializable - preferably JSON-LD to support interoperability and machine
interpretation.

In addition to the Meta-Code we also create a cryptographic hash (the metahash) of the supplied
SEED-METADATA. It is used to bind metadata to the digital asset. We use a blake-3 multihash with
base32-encoding as cryptographic hash. If properties are supplied, their raw bytes payload or their
JCS serialized JSON data will be the sole input to the cryptographic hash. Else we use a space
seperated concatenation of the cleaned `name` and `description` fields as inputs.


!!! tip
    For reasons of reproducibility, applications that generate ISCCs, should
    prioritize metadata that is automatically extracted from the digital asset.

    If embedded metadata is not available or known to be unreliable an application should rely on
    external metadata or explicitly ask users to supply at least the `name`-field. Applications
    should then **first embed the user supplied metadata** into the asset **before calculating
    the ISCC-CODE**.

    If neither embedded  nor external metadata is available, the application may resort to use the
    normalized filename of the digital asset as value for the `name`-field. An application may also
    skip generation of a Meta-Code entirely and create an ISCC-CODE without a Meta-Code.
"""
import base64
import unicodedata
import jcs
from more_itertools import interleave, sliced
from blake3 import blake3
from typing import Optional, Union
import iscc_core as ic


def gen_meta_code(name, description=None, properties=None, bits=ic.core_opts.meta_bits):
    # type: (str, Optional[str], Optional[Properties], int) -> dict
    """
    Create an ISCC Meta-Code using the latest standard algorithm.

    :param str name: Name or title of the work manifested by the digital asset
    :param Union[str,bytes,None] description: Optional description for disambiguation
    :param int bits: Bit-length of resulting Meta-Code (multiple of 64)
    :return: ISCC object with Meta-Code and properties name, description, properties, metahash
    :rtype: dict
    """
    return gen_meta_code_v0(name, description=description, properties=properties, bits=bits)


def gen_meta_code_v0(name, description=None, properties=None, bits=ic.core_opts.meta_bits):
    # type: (str, Optional[str], Optional[ic.Properties], int) -> dict
    """
    Create an ISCC Meta-Code with the algorithm version 0.

    !!! note

        The input for the `properties` field can be:

        - Structured (JSON/JCS serializable) metadata
        - Raw bytes from a file header

    :param str name: Name or title of the work manifested by the digital asset
    :param Optional[str] description:
        A User presentable textual description of the digital asset for disambiguation purposes
        (may include markdown).
    :param Optional[Properties] properties: Use-Case or industry-specific metadata.
        Either JSON serializable structured data or a binary blob.
    :param int bits: Bit-length of resulting Meta-Code (multiple of 64)
    :return: ISCC object with possible fields: iscc, name, description, properties, metahash
    :rtype: dict
    """

    # 1. Normalize `name`
    name = "" if name is None else name
    name = clean_text(name)
    name = remove_newlines(name)
    name = trim_text(name, ic.core_opts.meta_trim_name)

    # 2. Normalize `description`
    description = "" if description is None else description
    description = clean_text(description)
    description = trim_text(description, ic.core_opts.meta_trim_description)

    # Calculate meta_code, metahash, and properties value for the different input cases
    if properties:
        if isinstance(properties, bytes):
            meta_code_digest = soft_hash_meta_v0(name, properties)
            metahash = ic.InstanceHasherV0(properties).multihash()
            properties_value = base64.b64encode(properties).decode("ascii")
        elif isinstance(properties, dict):
            payload = jcs.canonicalize(properties)
            meta_code_digest = soft_hash_meta_v0(name, payload)
            metahash = ic.InstanceHasherV0(payload).multihash()
            properties_value = properties
        else:
            raise TypeError(f"properties must be bytes or dict not {type(properties)}")
    else:
        payload = " ".join((name, description)).strip().encode("utf-8")
        meta_code_digest = soft_hash_meta_v0(name, description)
        metahash = ic.InstanceHasherV0(payload).multihash()
        properties_value = None

    meta_code = ic.encode_component(
        mtype=ic.MT.META,
        stype=ic.ST.NONE,
        version=ic.VS.V0,
        bit_length=bits,
        digest=meta_code_digest,
    )
    iscc = "ISCC:" + meta_code

    # Build result
    result = {"iscc": iscc}
    if name:
        result["name"] = name
    if description:
        result["description"] = description
    if properties_value:
        result["properties"] = properties_value

    result["metahash"] = metahash

    return result


def soft_hash_meta_v0(name, extra=None):
    # type: (str, Union[str,bytes,None]) -> bytes
    """
    Calculate simmilarity preserving 256-bit hash digest from asset metadata.

    Textual input should be stripped of markup, normalized and trimmed before hashing.
    Json metadata should be normalized with
    [JCS](https://tools.ietf.org/id/draft-rundgren-json-canonicalization-scheme-00.html)

    !!! note
        The processing algorithm depends on the type of the `extra` input.
        If the `extra` field is supplied and non-empty, we create separate hashes for
        `title` and `extra` and interleave them in 32-bit chunks:

        - If the input is `None` or an empty `str`/`bytes` object the Meta-Hash will
        be generated from the `title`-field only.

        - If the `extra`-input is a non-empty **text** string (str) the string is
        lower-cased and the processing unit is an utf-8 endoded character
        (possibly multibyte). The resulting hash is interleaved with the `title`-hash.

        - If the `extra`-input is a non-empty **bytes** object the processing is done
        bytewise and the resulting hash is interleaved with the `title`-hash.

    :param str name: Title of the work manifested in the digital asset
    :param Union[str,bytes,None] extra: Additional metadata for disambiguation
    :return: 256-bit simhash digest for Meta-Code
    :rtype: bytes
    """
    name = ic.collapse_text(name)
    name_n_grams = ic.sliding_window(name, width=ic.core_opts.meta_ngram_size_text)
    name_hash_digests = [blake3(s.encode("utf-8")).digest() for s in name_n_grams]
    simhash_digest = ic.similarity_hash(name_hash_digests)

    if extra in {None, "", b""}:
        return simhash_digest
    else:
        # Augment with interleaved hash for extra metadata
        if isinstance(extra, bytes):
            # Raw bytes are handled per byte
            extra_n_grams = ic.sliding_window(extra, width=ic.core_opts.meta_ngram_size_bytes)
            extra_hash_digests = [blake3(ngram).digest() for ngram in extra_n_grams]
        elif isinstance(extra, str):
            # Text is collapsed and handled per character (multibyte)
            extra = ic.collapse_text(extra)
            extra_n_grams = ic.sliding_window(extra, width=ic.core_opts.meta_ngram_size_text)
            extra_hash_digests = [blake3(s.encode("utf-8")).digest() for s in extra_n_grams]
        else:
            raise ValueError("parameter `extra` must be of type str or bytes!")

        extra_simhash_digest = ic.similarity_hash(extra_hash_digests)

        # Interleave first half of name and extra simhashes in 32-bit chunks
        chunks_simhash_digest = sliced(simhash_digest[:16], 4)
        chunks_extra_simhash_digest = sliced(extra_simhash_digest[:16], 4)
        interleaved = interleave(chunks_simhash_digest, chunks_extra_simhash_digest)
        simhash_digest = bytearray()
        for chunk in interleaved:
            simhash_digest += chunk

        simhash_digest = bytes(simhash_digest)

        return simhash_digest


def trim_text(text, nbytes):
    # type: (str, int) -> str
    """Trim text such that its utf-8 encoded size does not exceed `nbytes`."""
    return text.encode("utf-8")[:nbytes].decode("utf-8", "ignore").strip()


def remove_newlines(text):
    # type: (str) -> str
    """
    Remove newlines.

    The `name` field serves as a displayable title. We remove newlines and leading and trailing
    whitespace. We also collapse consecutive spaces to single spaces.

    :param text: Text for newline removal
    :return: Single line of text
    :rtype: str
    """
    return " ".join(text.split())


def clean_text(text):
    # type: (str) -> str
    """
    Clean text for display.

    - Normalize with NFKC normalization.
    - Remove Control Characters (except newlines)
    - Reduce multiple consecutive newlines to a maximum of two newlines
    - Strip leading and trailing whitespace
    """

    # Unicode normalize
    text = unicodedata.normalize("NFKC", text)

    # Remove control characters
    text = "".join(
        ch for ch in text if unicodedata.category(ch)[0] != "C" or ch in ic.core_opts.text_newlines
    )

    # Collapse more than two consecutive newlines
    chars = []
    newline_count = 0
    for c in text:
        if c in ic.core_opts.text_newlines:
            if newline_count < 2:
                chars.append("\n")
                newline_count += 1
            continue
        else:
            newline_count = 0
        chars.append(c)
    text = "".join(chars)

    return text.strip()
