# -*- coding: utf-8 -*-
import os
import io
import blake3
from typing import Optional
from iscc_core.base import Data, Stream


BUFFER_SIZE = os.getenv("ISCC_BUFFER_SIZE", io.DEFAULT_BUFFER_SIZE)


def hash_instance(stream: Stream) -> bytes:
    data = stream.read(BUFFER_SIZE)
    hasher = InstanceHasher(data)
    while data:
        data = stream.read(BUFFER_SIZE)
        hasher.push(data)
    return hasher.digest()


class InstanceHasher:
    def __init__(self, data: Optional[Data] = None):
        self.hasher = blake3.blake3(data)

    def push(self, data: Data) -> None:
        self.hasher.update(data)

    def digest(self):
        return self.hasher.digest()
