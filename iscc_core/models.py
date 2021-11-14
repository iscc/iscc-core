# -*- coding: utf-8 -*-
"""Schema of objects returned by ISCC processing algorithms"""
from typing import List, Optional
from pydantic import BaseModel, Field


class DataCode(BaseModel):

    code: str = Field(..., description="Data-Code in standard representation.")
    features: Optional[List[str]] = Field(description="List of per datachunk hashes")
    sizes: Optional[List[int]] = Field(description="Sizes of datachunks")


class InstanceCode(BaseModel):

    code: str = Field(..., description="Instance-Code in standard representation.")
    datahash: str = Field(description="Multihash of digital asset (Blake3 by default.")
    filesize: int = Field(description="File size in bytes.")
