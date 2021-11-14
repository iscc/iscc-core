# -*- coding: utf-8 -*-
"""
*A similarity perserving hash for binary data (soft hash).*
"""
from typing import List, Optional, Tuple
from more_itertools import chunked
from iscc_core.cdc import data_chunks
from iscc_core.minhash import minhash_256, minhash_64
from iscc_core import codec
from iscc_core.codec import Data, Stream, encode_base64
from iscc_core.options import opts
from iscc_core.models import DataCode
import xxhash


def gen_data_code(stream, bits=opts.data_bits, granular=opts.data_granular):
    # type: (Stream, int) -> DataCode
    """
    Create a similarity preserving ISCC Data-Code with the latest standard algorithm.

    :param Stream stream: Input data stream.
    :param int bits: Bit-length of ISCC Data-Code (default 64).
    :param bool granular: Calculate additional granular data-features
    :return: ISCC Data-Code with properties: code, features, sizes
    :rtype: DataCode
    """
    return gen_data_code_v0(stream, bits, granular)


def gen_data_code_v0(stream, bits=opts.data_bits, granular=opts.data_granular):
    # type: (Stream, int) -> DataCode
    """
    Create an ISCC Data-Code with algorithm v0.

    :param Stream stream: Input data stream.
    :param int bits: Bit-length of ISCC Data-Code (default 64).
    :param bool granular: Calculate additional granular data-features
    :return: ISCC DataCode with properties: code, features, sizes
    :rtype: DataCode
    """
    features, sizes = None, None
    result = soft_hash_data_v0(stream, granular=granular)
    if granular:
        digest, features, sizes = result
    else:
        digest = result

    data_code = codec.encode_component(
        mtype=codec.MT.DATA,
        stype=codec.ST.NONE,
        version=codec.VS.V0,
        length=bits,
        digest=digest,
    )
    data_code_obj = DataCode(
        code=data_code,
    )

    if granular:
        data_code_obj.features = features
        data_code_obj.sizes = sizes

    return data_code_obj


def soft_hash_data_v0(stream, granular=opts.data_granular):
    # type: (Stream) -> Union[bytes, Tuple[bytes, List[str], List[int]]]
    """
    Create a similarity preserving Data-Hash digest

    :param stream: Input data stream.
    :param bool granular: Calculate additional granular data-features
    :return: 256-bit data soft-hash (if granular: a tuple of digest, features, sizes)
    :rtype: Union[bytes, Tuple[bytes, List[str], List[int]]]
    """
    hasher = DataHasherV0()
    data = stream.read(opts.cdc_read_size)

    while data:
        hasher.push(data)
        data = stream.read(opts.cdc_read_size)

    if granular is False:
        return hasher.digest()
    elif granular is True:
        return hasher.digest(), hasher.features(), hasher.sizes()
    else:
        raise ValueError("parameter granular must be True or False")


class DataHasherV0:
    """Incremental Data-Hash generator."""

    def __init__(self, data=None):
        # type: (Optional[Data]) -> None
        self.chunk_features = []
        self.chunk_sizes = []
        self.tail = None
        data = data or b""
        self.push(data)

    def push(self, data):
        # type: (Data) -> None
        """Push data to the Data-Hash generator."""
        if self.tail:
            data = self.tail + data

        for chunk in data_chunks(
            data, utf32=False, avg_chunk_size=opts.data_avg_chunk_size
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
        return minhash_256(self.chunk_features)

    def features(self):
        # type: () -> List[str]
        """Calculate and encode granular feature hashes.

        :return: Base64 encoded granular features (64-bit soft hashes)
        :rtype: List[str]
        """
        self._finalize()
        encoded_features = [
            encode_base64(minhash_64(cf))
            for cf in chunked(self.chunk_features, opts.data_granular_factor)
        ]
        return encoded_features

    def sizes(self):
        # type: () -> List[int]
        """Calculate sizes of granular feature chunks

        :return: List of sizes of granular features in number of bytes
        :rtype: List[int]
        """
        self._finalize()
        sizes = [sum(fh) for fh in chunked(self.chunk_sizes, opts.data_granular_factor)]
        return sizes

    def _finalize(self):
        if self.tail is not None:
            self.chunk_features.append(xxhash.xxh32_intdigest(self.tail))
            self.chunk_sizes.append(len(self.tail))
            self.tail = None


DataHasher = DataHasherV0
