# -*- coding: utf-8 -*-
import blake3
from typing import Optional, Tuple
from iscc_core.options import core_opts
from iscc_core import codec
from iscc_core.codec import Data, Stream
from iscc_core.schema import InstanceCode


def gen_instance_code(stream, bits=core_opts.instance_bits):
    # type: (Stream, int) -> InstanceCode
    """
    Create an ISCC Instance-Code with the latest standard algorithm.

    :param Stream stream: Binary data stream for Instance-Code generation
    :param int bits: Bit-length resulting Instance-Code (multiple of 64)
    :return: InstanceCode with properties: code, datahash, filesize
    :rtype: InstanceCode
    """
    return gen_instance_code_v0(stream, bits)


def gen_instance_code_v0(stream, bits=core_opts.instance_bits):
    # type: (Stream, int) -> InstanceCode
    """
    Create an ISCC Instance-Code with algorithm v0.

    :param Stream stream: Binary data stream for Instance-Code generation
    :param int bits: Bit-length of resulting Instance-Code (multiple of 64)
    :return: InstanceCode with properties: code, datahash, filesize
    :rtype: InstanceCode
    """
    hasher = InstanceHasherV0()
    data = stream.read(core_opts.io_read_size)
    while data:
        hasher.push(data)
        data = stream.read(core_opts.io_read_size)

    instance_code_obj = InstanceCode(
        iscc=hasher.code(bits=bits),
        datahash=hasher.digest().hex(),
        filesize=hasher.filesize,
    )

    return instance_code_obj


def hash_instance_v0(stream):
    # type: (Stream) -> bytes
    """
    Create 256-bit hash digest for the Instance-Code body

    :param Stream stream: Binary data stream for hash generation.
    :return: 256-bit Instance-Hash digest used as body of Instance-Code
    :rtype: bytes
    """
    hasher = InstanceHasherV0()
    data = stream.read(core_opts.io_read_size)
    while data:
        hasher.push(data)
        data = stream.read(core_opts.io_read_size)
    return hasher.digest()


class InstanceHasherV0:
    """
    Incremental Instance-Hash generator.
    """

    def __init__(self, data=None):
        # type: (Optional[Data]) -> None
        self.hasher = blake3.blake3()
        self.filesize = 0
        data = data or b""
        self.push(data)

    def push(self, data):
        # type: (Data) -> None
        """
        Push data to the Instance-Hash generator.

        :param Data data: Data to be hashed
        """
        self.filesize += len(data)
        self.hasher.update(data)

    def digest(self):
        # type: () -> bytes
        """
        Return Instance-Hash

        :return: Instance-Hash digest
        :rtype: bytes
        """
        return self.hasher.digest()

    def code(self, bits=core_opts.instance_bits):
        # type: (int) -> str
        """
        Encode digest as an ISCC Instance-Code component.

        :param int bits: Number of bits for the ISCC Instance-Code
        :return: ISCC Instance-Code
        :rtype: str
        """
        instance_code = codec.encode_component(
            mtype=codec.MT.INSTANCE,
            stype=codec.ST.NONE,
            version=codec.VS.V0,
            length=bits,
            digest=self.digest(),
        )
        return instance_code


InstanceHasher = InstanceHasherV0
