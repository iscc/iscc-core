import unicodedata
import jcs
from more_itertools import interleave, sliced
from blake3 import blake3
from typing import Optional, Union
from data_url import DataURL
import iscc_core as ic


__all__ = [
    "gen_meta_code",
    "gen_meta_code_v0",
    "soft_hash_meta_v0",
    "text_trim",
    "text_remove_newlines",
    "text_clean",
]


def gen_meta_code(name, description=None, meta=None, bits=ic.core_opts.meta_bits):
    # type: (str, Optional[str], Optional[ic.Meta], int) -> dict
    """
    Create an ISCC Meta-Code using the latest standard algorithm.

    :param str name: Name or title of the work manifested by the digital asset
    :param Optional[str] description: Optional description for disambiguation
    :param Optional[Union[dict,str] meta: Dict or Data-URL string with extended metadata
    :param int bits: Bit-length of resulting Meta-Code (multiple of 64)
    :return: ISCC object with Meta-Code and properties name, description, properties, metahash
    :rtype: dict
    """
    return gen_meta_code_v0(name, description=description, meta=meta, bits=bits)


def gen_meta_code_v0(name, description=None, meta=None, bits=ic.core_opts.meta_bits):
    # type: (str, Optional[str], Optional[ic.Meta], int) -> dict
    """
    Create an ISCC Meta-Code with the algorithm version 0.

    :param str name: Name or title of the work manifested by the digital asset
    :param Optional[str] description: Optional description for disambiguation
    :param Optional[Union[dict,str] meta: Dict or Data-URL string with extended metadata
    :param int bits: Bit-length of resulting Meta-Code (multiple of 64)
    :return: ISCC object with possible fields: iscc, name, description, metadata, metahash
    :rtype: dict
    """

    # 1. Normalize `name`
    name = "" if name is None else name
    name = text_clean(name)
    name = text_remove_newlines(name)
    name = text_trim(name, ic.core_opts.meta_trim_name)

    if not name:
        raise ValueError("Meta-Code requires non-empty name element (after normalization)")

    # 2. Normalize `description`
    description = "" if description is None else description
    description = text_clean(description)
    description = text_trim(description, ic.core_opts.meta_trim_description)

    # Calculate meta_code, metahash, and output metadata values for the different input cases
    if meta:
        if isinstance(meta, str):
            # Data-URL expected
            durl = meta
            payload = DataURL.from_url(durl).data
            meta_code_digest = soft_hash_meta_v0(name, payload)
            metahash = ic.multi_hash_blake3(payload)
            metadata_value = durl
        elif isinstance(meta, dict):
            payload = jcs.canonicalize(meta)
            meta_code_digest = soft_hash_meta_v0(name, payload)
            metahash = ic.multi_hash_blake3(payload)
            media_type = "application/ld+json" if "@context" in meta else "application/json"
            durl_obj = DataURL.from_data(media_type, base64_encode=True, data=payload)
            metadata_value = durl_obj.url
        else:
            raise TypeError(f"metadata must be Data-URL string or dict not {type(meta)}")
    else:
        payload = " ".join((name, description)).strip().encode("utf-8")
        meta_code_digest = soft_hash_meta_v0(name, description)
        metahash = ic.multi_hash_blake3(payload)
        metadata_value = None

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
    if metadata_value:
        result["meta"] = metadata_value

    result["metahash"] = metahash

    return result


def soft_hash_meta_v0(name, extra=None):
    # type: (str, Union[str,bytes,None]) -> bytes
    """
    Calculate simmilarity preserving 256-bit hash digest from asset metadata.

    Textual input should be stripped of markup, normalized and trimmed before hashing.
    Bytes input can be any serialized metadata (JSON, XML, Image...). Metadata should be
    serialized in a canonical form (for example
    [JCS](https://tools.ietf.org/id/draft-rundgren-json-canonicalization-scheme-00.html) for JSON)

    !!! note
        The processing algorithm depends on the type of the `extra` input.
        If the `extra` field is supplied and non-empty, we create separate hashes for
        `name` and `extra` and interleave them in 32-bit chunks:

        - If the `extra` input is `None` or an empty `str`/`bytes` object the Meta-Hash will
        be generated from the `name`-field only.

        - If the `extra`-input is a non-empty **text** string (str) the string is
        lower-cased and the processing units are utf-8 endoded characters (possibly multibyte).

        - If the `extra`-input is a non-empty **bytes** object the processing is done bytewise.


    :param str name: Title of the work manifested in the digital asset
    :param Union[str,bytes,None] extra: Additional metadata for disambiguation
    :return: 256-bit simhash digest for Meta-Code
    :rtype: bytes
    """
    name = ic.text_collapse(name)
    name_n_grams = ic.sliding_window(name, width=ic.core_opts.meta_ngram_size_text)
    name_hash_digests = [blake3(s.encode("utf-8")).digest() for s in name_n_grams]
    simhash_digest = ic.alg_simhash(name_hash_digests)

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
            extra = ic.text_collapse(extra)
            extra_n_grams = ic.sliding_window(extra, width=ic.core_opts.meta_ngram_size_text)
            extra_hash_digests = [blake3(s.encode("utf-8")).digest() for s in extra_n_grams]
        else:
            raise ValueError("parameter `extra` must be of type str or bytes!")

        extra_simhash_digest = ic.alg_simhash(extra_hash_digests)

        # Interleave first half of name and extra simhashes in 32-bit chunks
        chunks_simhash_digest = sliced(simhash_digest[:16], 4)
        chunks_extra_simhash_digest = sliced(extra_simhash_digest[:16], 4)
        interleaved = interleave(chunks_simhash_digest, chunks_extra_simhash_digest)
        simhash_digest = bytearray()
        for chunk in interleaved:
            simhash_digest += chunk

        simhash_digest = bytes(simhash_digest)

        return simhash_digest


def text_trim(text, nbytes):
    # type: (str, int) -> str
    """Trim text such that its utf-8 encoded size does not exceed `nbytes`."""
    return text.encode("utf-8")[:nbytes].decode("utf-8", "ignore").strip()


def text_remove_newlines(text):
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


def text_clean(text):
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
