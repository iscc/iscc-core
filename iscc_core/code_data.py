# -*- coding: utf-8 -*-
"""*A similarity perserving hash for binary data (soft hash).*"""
from typing import Optional
import xxhash
import iscc_core as ic

__all__ = [
    "gen_data_code",
    "gen_data_code_v0",
    "soft_hash_data_v0",
    "DataHasher",
    "DataHasherV0",
]


def gen_data_code(stream, bits=ic.core_opts.data_bits):
    # type: (ic.Stream, int) -> dict
    """
    Create a similarity preserving ISCC Data-Code with the latest standard algorithm.

    :param Stream stream: Input data stream.
    :param int bits: Bit-length of ISCC Data-Code (default 64).
    :return: ISCC Data-Code
    :rtype: dict
    """
    return gen_data_code_v0(stream, bits)


def gen_data_code_v0(stream, bits=ic.core_opts.data_bits):
    # type: (ic.Stream, int) -> dict
    """
    Create an ISCC Data-Code with algorithm v0.

    :param Stream stream: Input data stream.
    :param int bits: Bit-length of ISCC Data-Code (default 64).
    :return: ISCC object with Data-Code
    :rtype: dict
    """

    hasher = DataHasherV0()
    data = stream.read(ic.core_opts.io_read_size)

    while data:
        hasher.push(data)
        data = stream.read(ic.core_opts.io_read_size)

    data_code = hasher.code(bits=bits)
    iscc = "ISCC:" + data_code
    return dict(iscc=iscc)


def soft_hash_data_v0(stream):
    # type: (ic.Stream) -> bytes
    """
    Create a similarity preserving Data-Hash digest

    :param Stream stream: Input data stream.
    :return: 256-bit Data-Hash (soft-hash) digest used as body for Data-Code
    :rtype: bytes
    """
    hasher = DataHasherV0()
    data = stream.read(ic.core_opts.io_read_size)

    while data:
        hasher.push(data)
        data = stream.read(ic.core_opts.io_read_size)
    return hasher.digest()


class DataHasherV0:
    """Incremental Data-Hash generator."""

    def __init__(self, data=None):
        # type: (Optional[ic.Data]) -> None
        """
        Create a DataHasher

        :param Optional[Data] data: initial payload for hashing.
        """
        self.chunk_features = []
        self.chunk_sizes = []
        self.tail = None
        data = data or b""
        self.push(data)

    def push(self, data):
        # type: (ic.Data) -> None
        """Push data to the Data-Hash generator."""
        if self.tail:
            data = self.tail + data

        for chunk in ic.alg_cdc_chunks(
            data, utf32=False, avg_chunk_size=ic.core_opts.data_avg_chunk_size
        ):
            self.chunk_sizes.append(len(chunk))
            self.chunk_features.append(xxhash.xxh32_intdigest(chunk))
            self.tail = chunk  # Last chunk may not be final

        self.chunk_features = self.chunk_features[:-1]
        self.chunk_sizes = self.chunk_sizes[:-1]

    def digest(self):
        # type: () -> bytes
        """Calculate 256-bit minhash digest from feature hashes."""
        self._finalize()
        return ic.alg_minhash_256(self.chunk_features)

    def code(self, bits=ic.core_opts.data_bits):
        # type: (int) -> str
        """
        Encode digest as an ISCC Data-Code unit.

        :param int bits: Number of bits for the ISCC Data-Code
        :return: ISCC Data-Code
        :rtype: str
        """
        data_code = ic.encode_component(
            mtype=ic.MT.DATA,
            stype=ic.ST.NONE,
            version=ic.VS.V0,
            bit_length=bits,
            digest=self.digest(),
        )
        return data_code

    def _finalize(self):
        if self.tail is not None:
            self.chunk_features.append(xxhash.xxh32_intdigest(self.tail))
            self.chunk_sizes.append(len(self.tail))
            self.tail = None


DataHasher = DataHasherV0
