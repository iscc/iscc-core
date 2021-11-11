# -*- coding: utf-8 -*-
import mmap
from io import BufferedReader, BytesIO
from typing import BinaryIO, Union


# Types
Data = Union[bytes, bytearray, memoryview]
Stream = Union[BinaryIO, mmap.mmap, BytesIO, BufferedReader]
