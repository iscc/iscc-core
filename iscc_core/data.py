# -*- coding: utf-8 -*-
import io
from typing import Optional
from iscc_core.base import Data, Stream


def hash_data(stream: Stream) -> bytes:
    pass


class DataHasher:
    def __init__(self, data: Optional[Data]):
        self.buffer = b""
        if data:
            self.push(data)

    def push(self, data: Optional[Data]):
        pass


if __name__ == "__main__":
    pass

d = io.BytesIO()
print(d.read())
