# -*- coding: utf-8 -*-
"""*Schema of objects returned by ISCC processing algorithms.*

The schemata define standard fields to be set by ISCC generating applications.
This library only sets the fields for which information is available within the scope
of this library. Gathering and providing values for most of the fields is left to higher
level applications that handle format specific data extraction.
"""
import io
from typing import Dict, List, Optional, Union
from pydantic import BaseModel, Field, AnyUrl, HttpUrl
from iscc_core.codec import Code
from iscc_core.utils import canonicalize, ipfs_hash
from iscc_core import __version__


MultiStr = Union[str, List[str]]


class ISCC(BaseModel):
    """
    ISCC Metadata Schema
    """

    context: AnyUrl = Field(
        f"https://purl.org/iscc/context/{__version__}.json",
        description="JSON-LD Context URI",
        alias="@context",
        const=True,
    )

    type: AnyUrl = Field(
        f"https://purl.org/iscc/schema/{__version__}.json",
        description="JSON Schema URI",
        const=True,
    )

    iscc: str = Field(..., description="ISCC in canonical encoding.")

    # Essential metadata (ERC-721/ERC-1155 compatible)
    name: Optional[str] = Field(
        description="The name or title of the intangible creation manifested by the"
        " identified digital asset",
    )

    description: Optional[str] = Field(
        description="Description of the digital asset identified by the ISCC (used "
        "as input for Meta-Code generation). Any user presentable text string (includ"
        "ing Markdown text) indicative of the identity of the referent may be used. ",
    )

    image: Optional[AnyUrl] = Field(
        description="URI for a user presentable image that serves as a preview of "
        "identified digital content or, in case of an NFT, the digital content itself.",
    )

    keywords: Optional[List[str]] = Field(
        description="List of keywords relevant to the identified digital content.",
    )

    identifier: Optional[Union[str, List[str]]] = Field(
        description="Other identifier(s) such as those defined by ISO/TC 46/SC 9 "
        "referencing the work, product or other abstraction of which the referenced "
        "digital asset is a full or partial manifestation.",
        context=f"https://purl.org/iscc/context/{__version__}/identifier",
    )

    # File Properties
    filename: Optional[str] = Field(
        description="Filename of the referenced digital asset (automatically used as "
        "fallback if no seed_title element is specified)",
        context="https://dbpedia.org/ontology/filename",
    )

    filesize: Optional[int] = Field(
        description="File size of media asset in bytes.",
        context="https://dbpedia.org/ontology/fileSize",
    )

    mediatype: Optional[str] = Field(
        description="IANA Media Type (MIME type)",
        context="encodingFormat",
    )

    # Cryptographic hashes
    tophash: Optional[str] = Field(
        title="tophash",
        description="Blake3 hash over concatenation of metahash and datahash",
    )
    metahash: Optional[str] = Field(
        title="metahash", description="Blake3 hash of metadata."
    )
    datahash: Optional[str] = Field(
        title="datahash", description="Blake3 hash of media file."
    )

    # Essential Media Properties
    duration: Optional[float] = Field(
        description="Duration of audio-visual media in secondes."
    )
    fps: Optional[float] = Field(description="Frames per second of video assets.")
    width: Optional[int] = Field(description="Width of visual media in pixels.")
    height: Optional[int] = Field(description="Height of visual media in pixels.")
    characters: Optional[int] = Field(
        description="Number of text characters (code points after Unicode "
        "normalization)"
    )
    language: Optional[Union[str, List[str]]] = Field(
        description="Language(s) of content (BCP-47) in weighted order.",
        context="inLanguage",
    )

    parts: Optional[List[str]] = Field(description="Included Content-Codes.")

    license: Optional[AnyUrl] = Field(
        description="URI of license for the identified digital content."
    )

    redirect: Optional[HttpUrl] = Field(
        description="URL to which a resolver should redirect an ISCC-ID that has "
        "been minted from a declartion that includes the IPFS-hash of this metadata "
        "instance."
    )

    def dict(self, *args, exclude_none=True, by_alias=True, **kwargs):
        """
        Exclude empty fields and support @context alias.

        !!! note
            This overides the default BaseModel.dict()
        """
        return super().dict(
            *args,
            exclude_none=exclude_none,
            by_alias=by_alias,
            **kwargs,
        )

    def dict_raw(self):
        """Exclude any versioned properties (used mostly for testing)"""
        return self.dict(exclude={"context", "type"})

    def json(self, *args, exclude_none=True, by_alias=True, **kwargs):
        """
        Exclude empty fields and use @context alias.

        The by_alias=True allows us to generate valid JSON-LD by default. It translates
        our python "context" property to @context

        !!! note
            This overides the default BaseModel.json()
        """
        return super().json(
            *args,
            exclude_none=exclude_none,
            by_alias=by_alias,
            **kwargs,
        )

    @property
    def code(self):
        # type: () -> str
        """Code without `ISCC:`-prefix"""
        return self.iscc.lstrip("ISCC:")

    @property
    def code_obj(self):
        # type: () -> Code
        """Wraps the `iscc` string property with a `Code` object."""
        return Code(self.iscc)

    def jcs(self):
        # type: () -> bytes
        """
        Serialize metadata in conformance with JCS (RFC 8785) JSON canonicalization.

        Used as payload for cryptographic hashing.
        """
        obj = self.dict(by_alias=True, exclude_none=True)
        return canonicalize(obj)

    def jsonld_norm(self):
        """
        Returns `URDNA2015` normalized JSON-LD in `application/n-quads` format.

        Used for cryptographically binding assertions from metadata
        """
        from pyld import jsonld

        jsonld.set_document_loader(jsonld.requests_document_loader(timeout=10))

        data = self.dict()
        data["iscc"] = "ISCC:" + data["iscc"]

        return jsonld.normalize(
            data, {"algorithm": "URDNA2015", "format": "application/n-quads"}
        )

    def ipfs_hash(self):
        # type: () -> str
        """
        Create canonical IPFS hash for ISCC metadata
        """
        return ipfs_hash(io.BytesIO(self.jcs()))

    @classmethod
    def jsonld_context(cls):
        # type: () -> Dict
        """
        Build JSON-LD context from ISCC model for publishing

        :return: Serialized JSON-LD context for publishing.
        :rtype: str
        """
        wrapper = {
            "@context": [
                "https://schema.org/docs/jsonldcontext.jsonld",
                {
                    "type": "@type",
                    "iscc": "@id",
                },
            ]
        }
        ctx = wrapper["@context"][1]
        for prop, fields in cls.schema()["properties"].items():
            if "context" in fields:
                ctx[prop] = fields["context"]

        return wrapper
