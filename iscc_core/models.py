# -*- coding: utf-8 -*-
"""Schema of objects returned by ISCC processing algorithms"""
from typing import List, Optional, Union
from pydantic import BaseModel, Field


MultiStr = Union[str, List[str]]


class TextCode(BaseModel):
    """TextCode standardized plaintext metadata model."""

    code: str = Field(..., description="Text-Code in standard representation.")
    title: Optional[str] = Field(description="Title as extracted from text document")
    characters: Optional[int] = Field(
        description="Number of text characters (after normalize_text)"
    )
    language: Optional[str] = Field(description="Main language of content (BCP-47)")
    features: Optional[List[str]] = Field(description="List of hashes per text chunk")
    sizes: Optional[List[int]] = Field(description="Sizes of text chunks in characters")


class VideoCode(BaseModel):
    """VideoCode standardized asset metadata model."""

    code: str = Field(..., description="Video-Code in standard representation.")
    title: Optional[str] = Field(description="Title as extracted from video asset")
    duration: Optional[float] = Field(description="Duration of video im seconds")
    fps: Optional[float] = Field(description="Frames per second")
    width: Optional[int] = Field(description="Width of video in number of pixels")
    height: Optional[int] = Field(description="Height of video in number of pixels")
    language: Optional[MultiStr] = Field(description="Main language of video (BCP 47)")


class DataCode(BaseModel):
    """DataCode standardized asset metadata model."""

    code: str = Field(..., description="Data-Code in standard representation.")
    features: Optional[List[str]] = Field(description="List of per datachunk hashes")
    sizes: Optional[List[int]] = Field(description="Sizes of datachunks")


class InstanceCode(BaseModel):
    """InstanceCode standardized asset metadata model."""

    code: str = Field(..., description="Instance-Code in standard representation.")
    datahash: str = Field(description="Multihash of digital asset (Blake3 by default.")
    filesize: int = Field(description="File size in bytes.")
