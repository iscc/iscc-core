# -*- coding: utf-8 -*-
"""*A data checksum.*"""
from blake3 import blake3
from typing import Optional
import iscc_core as ic


__all__ = [
    "gen_instance_code",
    "gen_instance_code_v0",
    "hash_instance_v0",
    "InstanceHasher",
    "InstanceHasherV0",
]


def gen_instance_code(stream, bits=ic.core_opts.instance_bits):
    # type: (ic.Stream, int) -> dict
    """
    Create an ISCC Instance-Code with the latest standard algorithm.

    :param Stream stream: Binary data stream for Instance-Code generation
    :param int bits: Bit-length resulting Instance-Code (multiple of 64)
    :return: ISCC object with properties: iscc, datahash, filesize
    :rtype: dict
    """
    return gen_instance_code_v0(stream, bits)


def gen_instance_code_v0(stream, bits=ic.core_opts.instance_bits):
    # type: (ic.Stream, int) -> dict
    """
    Create an ISCC Instance-Code with algorithm v0.

    :param Stream stream: Binary data stream for Instance-Code generation
    :param int bits: Bit-length of resulting Instance-Code (multiple of 64)
    :return: ISCC object with Instance-Code and properties: datahash, filesize
    :rtype: dict
    """
    hasher = InstanceHasherV0()
    data = stream.read(ic.core_opts.io_read_size)
    while data:
        hasher.push(data)
        data = stream.read(ic.core_opts.io_read_size)

    instance_code = hasher.code(bits=bits)
    iscc = "ISCC:" + instance_code
    instance_code_obj = dict(
        iscc=iscc,
        datahash=hasher.multihash(),
        filesize=hasher.filesize,
    )

    return instance_code_obj


def hash_instance_v0(stream):
    # type: (ic.Stream) -> bytes
    """
    Create 256-bit hash digest for the Instance-Code body

    :param Stream stream: Binary data stream for hash generation.
    :return: 256-bit Instance-Hash digest used as body of Instance-Code
    :rtype: bytes
    """
    hasher = InstanceHasherV0()
    data = stream.read(ic.core_opts.io_read_size)
    while data:
        hasher.push(data)
        data = stream.read(ic.core_opts.io_read_size)
    return hasher.digest()


class InstanceHasherV0:
    """Incremental Instance-Hash generator."""

    #: Multihash prefix
    mh_prefix: bytes = b"\x1e\x20"

    def __init__(self, data=None):
        # type: (Optional[ic.Data]) -> None
        self.hasher = blake3(max_threads=blake3.AUTO)
        self.filesize = 0
        data = data or b""
        self.push(data)

    def push(self, data):
        # type: (ic.Data) -> None
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

    def multihash(self):
        # type: () -> str
        """
        Return blake3 multihash

        :return: Blake3 hash as 256-bit multihash
        :rtype: str
        """
        return (self.mh_prefix + self.digest()).hex()

    def code(self, bits=ic.core_opts.instance_bits):
        # type: (int) -> str
        """
        Encode digest as an ISCC Instance-Code unit.

        :param int bits: Number of bits for the ISCC Instance-Code
        :return: ISCC Instance-Code
        :rtype: str
        """
        instance_code = ic.encode_component(
            mtype=ic.MT.INSTANCE,
            stype=ic.ST.NONE,
            version=ic.VS.V0,
            bit_length=bits,
            digest=self.digest(),
        )
        return instance_code


InstanceHasher = InstanceHasherV0
