# -*- coding: utf-8 -*-
"""Schema of objects returned by ISCC processing algorithms.

The schemata define standard fields to be set by ISCC generating applications.
This library only sets the fields for which information is available within the scope
of this library. Gathering and providing values for most of the fields is left to higher
level applications that handle format specific data extraction.
"""
from typing import List, Optional, Union
from pydantic import BaseModel, Field
from iscc_core.codec import Code
import abc


MultiStr = Union[str, List[str]]


class IsccBase(BaseModel, abc.ABC):
    """Base schema for ISCC metadata"""

    class Config:
        validate_assignment = True

    iscc: str = Field(..., description="ISCC in standard encoding.")

    @property
    def code_obj(self):
        """Wraps the `iscc` string property with a `Code` object."""
        return Code(self.iscc)

    def dict(self, *args, exclude_unset=True, exclude_none=True, **kwargs):
        """Change default options to exclude unset and none values."""
        return super().dict(
            *args, exclude_unset=exclude_unset, exclude_none=exclude_none, **kwargs
        )


class IsccCode(IsccBase):
    """A composite ISCC"""

    version: str = Field(
        "0-0-0",
        title="ISCC Schema Version",
        description="Version of ISCC Metadata Schema (SchemaVer).",
        const=True,
    )

    # Essential Metadata
    title: Optional[str] = Field(
        description="The title or name of the intangible creation manifested by the"
        " identified digital asset"
    )
    extra: Optional[str] = Field(
        description="Descriptive, industry-sector or use-case specific metadata (used "
        "as immutable input for Meta-Code generation). Any text string "
        "(including json or json-ld) indicative of the identity of the "
        "referent may be used."
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
    preview: Optional[str] = Field(description="Uri of media asset preview.")


class IsccID(IsccCode):
    """An ISCC Short-ID"""

    pass


class ContentCode(IsccBase, abc.ABC):
    """Base schema for Content-Codes."""

    title: Optional[str] = Field(description="Title as extracted from digital asset")


class MetaCode(IsccBase):
    """Meta-Code standardized metadata model."""

    title: Optional[str] = Field(description="Title used for Meta-Code creation.")
    extra: Optional[str] = Field(description="Extra metadata used for Meta-Code.")
    binary: Optional[bool] = Field(
        description="Extra metadata was supplied in binary format."
    )
    metahash: Optional[str] = Field(
        description="Blake3 cryptographic hash of metadata."
    )


class ContentCodeText(ContentCode):
    """Content-Code-Text standardized metadata model."""

    characters: Optional[int] = Field(
        description="Number of text characters (after normalize_text)."
    )
    language: Optional[str] = Field(description="Main language of content (BCP-47).")


class ContentCodeImage(ContentCode):
    """Content-Code-Image standardized metadata model."""

    width: Optional[int] = Field(description="Width of image in number of pixels.")
    height: Optional[int] = Field(description="Height of image in number of pixels.")
    preview: Optional[str] = Field(description="URI of image preview thumbnail.")


class ContentCodeAudio(ContentCode):
    """Content-Code-Audio standardized metadata model."""

    duration: Optional[float] = Field(description="Duration of audio im seconds.")


class ContentCodeVideo(ContentCode):
    """Content-Code-Video standardized metadata model."""

    duration: Optional[float] = Field(description="Duration of video im seconds.")
    fps: Optional[float] = Field(description="Frames per second.")
    width: Optional[int] = Field(description="Width of video in number of pixels.")
    height: Optional[int] = Field(description="Height of video in number of pixels.")
    language: Optional[MultiStr] = Field(description="Main language of video (BCP 47).")


class ContentCodeMixed(ContentCode):
    """Content-Code-Mixed standardized metadata model."""

    parts: Optional[List[str]] = Field(description="Included Content-Codes.")


class DataCode(IsccBase):
    """Data-Code standardized metadata model."""

    pass


class InstanceCode(IsccBase):
    """Instance-Code standardized metadata model."""

    datahash: Optional[str] = Field(
        description="Multihash of digital asset (Blake3 by default."
    )
    filesize: Optional[int] = Field(description="File size in bytes.")
