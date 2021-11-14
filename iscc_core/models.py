# -*- coding: utf-8 -*-
"""Schema of objects returned by ISCC processing algorithms"""
from typing import List, Optional, Union
from pydantic import BaseModel, Field
from iscc_core.codec import Code


MultiStr = Union[str, List[str]]


class BaseCode(BaseModel):
    @property
    def code_obj(self):
        return Code(self.code)


class MetaCode(BaseCode):
    """Meta-Code standardized metadata model."""

    code: str = Field(..., description="Meta-Code in standard representation.")
    title: Optional[str] = Field(description="Title used for Meta-Code creation.")
    extra: Optional[str] = Field(description="Extra metadata used for Meta-Code.")
    binary: bool = Field(description="Extra metadata was supplied in binary format.")
    metahash: str = Field(description="Blake3 cryptographic hash of metadata.")


class ContentCodeText(BaseCode):
    """Content-Code-Text standardized metadata model."""

    code: str = Field(..., description="Content-Code-Text in standard representation.")
    title: Optional[str] = Field(description="Title as extracted from text document.")
    characters: Optional[int] = Field(
        description="Number of text characters (after normalize_text)."
    )
    language: Optional[str] = Field(description="Main language of content (BCP-47).")


class ContentCodeImage(BaseCode):
    """Content-Code-Image standardized metadata model."""

    code: str = Field(..., description="Content-Code-Image in standard representation.")
    title: Optional[str] = Field(description="Title as extracted from image file.")
    width: Optional[int] = Field(description="Width of image in number of pixels.")
    height: Optional[int] = Field(description="Height of image in number of pixels.")


class ContentCodeAudio(BaseCode):
    """Content-Code-Audio standardized metadata model."""

    code: str = Field(..., description="Content-Code-Audio in standard representation.")
    title: Optional[str] = Field(description="Title as extracted from audio asset.")
    duration: Optional[float] = Field(description="Duration of audio im seconds.")


class ContentCodeVideo(BaseCode):
    """Content-Code-Video standardized metadata model."""

    code: str = Field(..., description="Content-Code-Video in standard representation.")
    title: Optional[str] = Field(description="Title as extracted from video asset.")
    duration: Optional[float] = Field(description="Duration of video im seconds.")
    fps: Optional[float] = Field(description="Frames per second.")
    width: Optional[int] = Field(description="Width of video in number of pixels.")
    height: Optional[int] = Field(description="Height of video in number of pixels.")
    language: Optional[MultiStr] = Field(description="Main language of video (BCP 47).")


class DataCode(BaseCode):
    """Data-Code standardized metadata model."""

    code: str = Field(..., description="Data-Code in standard representation.")
    features: Optional[List[str]] = Field(description="List of per datachunk hashes")
    sizes: Optional[List[int]] = Field(description="Sizes of datachunks")


class InstanceCode(BaseCode):
    """Instance-Code standardized metadata model."""

    code: str = Field(..., description="Instance-Code in standard representation.")
    datahash: str = Field(description="Multihash of digital asset (Blake3 by default.")
    filesize: int = Field(description="File size in bytes.")
