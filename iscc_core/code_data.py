# -*- coding: utf-8 -*-
from typing import Optional
from iscc_core.base import Data, Stream
from iscc_core.cdc import data_chunks
from iscc_core.base import CDC_READ_SIZE
from iscc_core.minhash import minhash_256
from iscc_core import codec
import xxhash


def code_data(stream, bits=64):
    # type: (Stream, int) -> str
    return code_data_v0(stream, bits)


def code_data_v0(stream, bits=64):
    # type: (Stream, int) -> str
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
    hasher = DataHasherV0()
    data = stream.read(CDC_READ_SIZE)

    while data:
        hasher.push(data)
        data = stream.read(CDC_READ_SIZE)

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

        for chunk in data_chunks(data):
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


print(DataHasher(b"\x00").digest().hex())
