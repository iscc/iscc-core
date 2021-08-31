# -*- coding: utf-8 -*-
from typing import Optional
from iscc_core.base import Data, Stream
from iscc_core.cdc import data_chunks
from iscc_core.base import CDC_READ_SIZE
from iscc_core.minhash import minhash_256
import xxhash


def hash_data(stream: Stream) -> bytes:
    return hash_data_v0(stream)


def hash_data_v0(stream: Stream) -> bytes:
    hasher = DataHasherV0()
    data = stream.read(CDC_READ_SIZE)

    while data:
        hasher.push(data)
        data = stream.read(CDC_READ_SIZE)

    return hasher.digest()


class DataHasherV0:
    def __init__(self, data: Optional[Data] = None):
        self.chunk_features = []
        self.chunk_sizes = []
        self.tail = None
        data = data or b""
        self.push(data)

    def push(self, data: Data):

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
        chunk_features = self.chunk_features
        chunk_sizes = self.chunk_sizes
        if self.tail is not None:
            chunk_features.append(xxhash.xxh32_intdigest(self.tail))
            chunk_sizes.append(len(self.tail))
            self.tail = None
        return minhash_256(chunk_features)


DataHasher = DataHasherV0


print(DataHasher(b"\x00").digest().hex())
