# -*- coding: utf-8 -*-
"""*Schema of objects returned by ISCC processing algorithms.*

The schemata define standard fields to be set by ISCC generating applications.
This library only sets the fields for which information is available within the scope
of this library. Gathering and providing values for most of the fields is left to higher
level applications that handle format specific data extraction.
"""
from typing import List, Optional, Union
from pydantic import BaseModel, Field, AnyUrl, HttpUrl
from iscc_core.codec import Code


MultiStr = Union[str, List[str]]


class ISCC(BaseModel):
    """
    ISCC Metadata Schema
    """

    version: str = Field(
        "0-0-0",
        title="ISCC Schema Version",
        description="Version of ISCC Metadata Schema (SchemaVer).",
        const=True,
    )

    iscc: str = Field(..., description="ISCC in standard encoding.")

    # Essential metadata (ERC-721/ERC-1155 compatible)
    name: Optional[str] = Field(
        description="The name or title of the intangible creation manifested by the"
        " identified digital asset"
    )

    description: Optional[str] = Field(
        description="Description of the digital asset identified by the ISCC (used "
        "as input for Meta-Code generation). Any user presentable text string (includ"
        "ing Markdown text) indicative of the identity of the referent may be used. "
    )

    image: Optional[AnyUrl] = Field(
        description="URI for a user presentable image that serves as a preview of "
        "identified digital content or, in case of an NFT, the digital content itself."
    )

    # File Properties
    filename: Optional[str] = Field(
        description="Filename of the referenced digital asset (automatically used as "
        "fallback if no seed_title element is specified)"
    )
    filesize: Optional[int] = Field(description="File size of media asset in bytes.")
    mediatype: Optional[str] = Field(description="IANA Media Type (MIME type)")

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
        description="Language(s) of content (BCP-47) in weighted order."
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

    @property
    def code_obj(self):
        """Wraps the `iscc` string property with a `Code` object."""
        return Code(self.iscc)

    def dict(self, *args, exclude_unset=True, exclude_none=True, **kwargs):
        """Exclude unset and none values by default."""
        return super().dict(
            *args, exclude_unset=exclude_unset, exclude_none=exclude_none, **kwargs
        )
