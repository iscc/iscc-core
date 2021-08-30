# -*- coding: utf-8 -*-
import os
import mmap
from io import BufferedReader, BytesIO
from typing import BinaryIO, Union


# Constants
CDC_READ_SIZE: int = os.getenv("CDC_READ_SIZE", 262144)
CDC_AVG_CHUNK_SIZE: int = os.getenv("CDC_AVG_CHUNK_SIZE", 1024)
INSTANCE_READ_SIZE: int = os.getenv("INSTANCE_READ_SIZE", 262144)


# Types
Data = Union[bytes, bytearray, memoryview]
Stream = Union[BinaryIO, mmap.mmap, BytesIO, BufferedReader]
