# -*- coding: utf-8 -*-
"""Schema of objects returned by ISCC processing algorithms"""
from typing import List, Optional, Union
from pydantic import BaseModel, Field
from iscc_core.codec import Code


MultiStr = Union[str, List[str]]


class BaseCode(BaseModel):
    """Base schema for codes."""

    code: str = Field(..., description="ISCC code in standard encoding.")

    @property
    def code_obj(self):
        return Code(self.code)


class MetaCode(BaseCode):
    """Meta-Code standardized metadata model."""

    extra: Optional[str] = Field(description="Extra metadata used for Meta-Code.")
    binary: bool = Field(description="Extra metadata was supplied in binary format.")
    metahash: str = Field(description="Blake3 cryptographic hash of metadata.")


class ContentCode(BaseCode):
    """Base schema for Content-Codes."""

    title: Optional[str] = Field(description="Title as extracted from digital asset")


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

    parts: List[str] = Field(description="Included Content-Codes.")


class DataCode(BaseCode):
    """Data-Code standardized metadata model."""

    features: Optional[List[str]] = Field(description="List of per datachunk hashes")
    sizes: Optional[List[int]] = Field(description="Sizes of datachunks")


class InstanceCode(BaseCode):
    """Instance-Code standardized metadata model."""

    datahash: str = Field(description="Multihash of digital asset (Blake3 by default.")
    filesize: int = Field(description="File size in bytes.")
