# -*- coding: utf-8 -*-
"""Schema of objects returned by ISCC processing algorithms"""
from pydantic import BaseModel, Field


class InstanceCode(BaseModel):
    code: str = Field(..., description="Instance-Code in standard representation.")
    datahash: str = Field(description="Multihash of digital asset (Blake3 by default.")
    filesize: int = Field(description="File size in bytes.")
