# -*- coding: utf-8 -*-
import blake3
from typing import Optional
from iscc_core.options import opts
from iscc_core import codec
from iscc_core.codec import Data, Stream


def gen_instance_code(stream, bits=opts.instance_bits):
    # type: (Stream, int) -> str
    """Create an ISCC Instance-Code with the latest standard algorithm

    :param Stream stream: Binary data stream for Instance-Code generation.
    :param int bits: Bit-length resulting Instance-Code (multiple of 64)
    :return: Instance-Code
    :rtype: str
    """
    return gen_instance_code_v0(stream, bits)


def gen_instance_code_v0(stream, bits=opts.instance_bits):
    # type: (Stream, int) -> str
    """Create an ISCC Instance-Code with algorithm v0

    :param Stream stream: Binary data stream for Instance-Code generation.
    :param int bits: Bit-length of resulting Instance-Code (multiple of 64)
    :return: Instance-Code
    :rtype: str
    """
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
    """Create 256-bit hash digest for the Instance-Code body

    :param Stream stream: Binary data stream for hash generation.
    :return: 256-bit Instance-Hash digest
    :rtype: bytes
    """
    hasher = InstanceHasherV0()
    data = stream.read(opts.instance_read_size)
    while data:
        hasher.push(data)
        data = stream.read(opts.instance_read_size)
    return hasher.digest()


class InstanceHasherV0:
    """Incremental Instance-Hash generator."""

    def __init__(self, data=None):
        # type: (Optional[Data]) -> None
        self.hasher = blake3.blake3()
        data = data or b""
        self.push(data)

    def push(self, data):
        # type: (Data) -> None
        """Push data to the Instance-Hash generator.

        :param Data data: Data to be hashed
        """
        self.hasher.update(data)

    def digest(self):
        # type: () -> bytes
        """Return Instance-Hash

        :return: Instance-Hash digest
        :rtype: bytes
        """
        return self.hasher.digest()


InstanceHasher = InstanceHasherV0
