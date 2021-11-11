# -*- coding: utf-8 -*-
from pydantic import BaseSettings, Field


class CoreOptions(BaseSettings):
    """Parameters with defaults for ISCC calculations."""

    class Config:
        env_file = "iscc-core.env"
        env_file_encoding = "utf-8"

    meta_bits: int = Field(64, description="Length of generated Meta-Code in bits")
    meta_trim_title: int = Field(
        128, description="Trim title length to this mumber of bytes"
    )
    meta_trim_extra: int = Field(4096, description="Trim extra to this number of bytes")
    meta_ngram_size_title: int = Field(
        3, description="Sliding window width (characters) for title metadata"
    )
    meta_ngram_size_extra_text: int = Field(
        3,
        description="Sliding window width (characters) for textural extra metadata",
    )
    meta_ngram_size_extra_binary: int = Field(
        3,
        description="Sliding window width (bytes) for binary extra metadata",
    )


opts = CoreOptions()
