# -*- coding: utf-8 -*-
import blake3
from typing import Optional
from iscc_core.base import Data, Stream, INSTANCE_READ_SIZE
from iscc_core import codec


def gen_instance_code(stream, bits=64):
    # type: (Stream, int) -> str
    """Create an ISCC Instance-Code with the latest standard algorithm"""
    return gen_instance_code_v0(stream, bits)


def gen_instance_code_v0(stream, bits=64):
    # type: (Stream, int) -> str
    """Create an ISCC Instance-Code with algorithm v0"""
    digest = hash_instance_v0(stream)
    instance_code = codec.encode_component(
        mtype=codec.MT.INSTANCE,
        stype=codec.ST.NONE,
        version=codec.VS.V0,
        length=bits,
        digest=digest,
    )
    return instance_code


def hash_instance_v0(stream):
    # type: (Stream) -> bytes
    """Create 256-bit hash for Instance-Code"""
    hasher = InstanceHasherV0()
    data = stream.read(INSTANCE_READ_SIZE)
    while data:
        hasher.push(data)
        data = stream.read(INSTANCE_READ_SIZE)
    return hasher.digest()


class InstanceHasherV0:
    def __init__(self, data=None):
        # type: (Optional[Data]) -> None
        self.hasher = blake3.blake3()
        data = data or b""
        self.push(data)

    def push(self, data):
        # type: (Data) -> None
        self.hasher.update(data)

    def digest(self):
        # type: () -> bytes
        return self.hasher.digest()


InstanceHasher = InstanceHasherV0
