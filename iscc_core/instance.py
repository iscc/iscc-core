# -*- coding: utf-8 -*-
import blake3
from typing import Optional
from iscc_core.base import Data, Stream, INSTANCE_READ_SIZE


def hash_instance(stream: Stream) -> bytes:
    return hash_instance_v0(stream)


def hash_instance_v0(stream: Stream) -> bytes:
    hasher = InstanceHasherV0()
    data = stream.read(INSTANCE_READ_SIZE)
    while data:
        hasher.push(data)
        data = stream.read(INSTANCE_READ_SIZE)
    return hasher.digest()


class InstanceHasherV0:
    def __init__(self, data: Optional[Data] = None):
        self.hasher = blake3.blake3()
        data = data or b''
        self.push(data)

    def push(self, data: Data) -> None:
        self.hasher.update(data)

    def digest(self):
        return self.hasher.digest()


InstanceHasher = InstanceHasherV0
