# -*- coding: utf-8 -*-
"""
*A similarity perserving hash for binary data (soft hash).*
"""
from typing import Optional
from iscc_core.cdc import data_chunks
from iscc_core.minhash import minhash_256
from iscc_core import codec
from iscc_core.codec import Data, Stream
from iscc_core.options import opts
import xxhash


def gen_data_code(stream, bits=opts.data_bits):
    # type: (Stream, int) -> str
    """
    Create a similarity preserving ISCC Data-Code with the latest standard algorithm.

    :param stream: Input data stream.
    :param int bits: Bit-length of ISCC Data-Code (default 64).
    :return: ISCC Data-Code
    :rtype: str
    """
    return gen_data_code_v0(stream, bits)


def gen_data_code_v0(stream, bits=opts.data_bits):
    # type: (Stream, int) -> str
    """
    Create an ISCC Data-Code with algorithm v0.

    :param stream: Input data stream.
    :param int bits: Bit-length of ISCC Data-Code (default 64).
    :return: str
    """

    digest = hash_data_v0(stream)
    data_code = codec.encode_component(
        mtype=codec.MT.DATA,
        stype=codec.ST.NONE,
        version=codec.VS.V0,
        length=bits,
        digest=digest,
    )
    return data_code


def hash_data_v0(stream):
    # type: (Stream) -> bytes
    """
    Create a similarity preserving Data-Hash digest

    :param stream: Input data stream.
    :return: Similarity preserving Data-Hash digest
    :rtype: bytes
    """
    hasher = DataHasherV0()
    data = stream.read(opts.cdc_read_size)

    while data:
        hasher.push(data)
        data = stream.read(opts.cdc_read_size)

    return hasher.digest()


class DataHasherV0:
    def __init__(self, data=None):
        # type: (Optional[Data]) -> None
        self.chunk_features = []
        self.chunk_sizes = []
        self.tail = None
        data = data or b""
        self.push(data)

    def push(self, data):
        # type: (Data) -> None
        if self.tail:
            data = self.tail + data

        for chunk in data_chunks(data, False):
            self.chunk_sizes.append(len(chunk))
            self.chunk_features.append(xxhash.xxh32_intdigest(chunk))

        # Last chunk may not be final
        self.tail = chunk
        self.chunk_features = self.chunk_features[:-1]
        self.chunk_sizes = self.chunk_sizes[:-1]

    def digest(self):
        # type: () -> bytes
        chunk_features = self.chunk_features
        chunk_sizes = self.chunk_sizes
        if self.tail is not None:
            chunk_features.append(xxhash.xxh32_intdigest(self.tail))
            chunk_sizes.append(len(self.tail))
            self.tail = None
        return minhash_256(chunk_features)


DataHasher = DataHasherV0
