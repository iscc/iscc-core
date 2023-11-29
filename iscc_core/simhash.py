# -*- coding: utf-8 -*-
from bitarray import bitarray


def alg_simhash(hash_digests):
    # type: (list[bytes]) -> bytes
    """
    Creates a similarity preserving hash from a sequence of equal sized hash digests.

    :param list hash_digests: A sequence of equally sized byte-hashes.
    :returns: Similarity byte-hash
    :rtype: bytes
    """

    n_bytes = len(hash_digests[0])
    n_bits = n_bytes * 8
    vector = [0] * n_bits

    for digest in hash_digests:
        h = bitarray()
        h.frombytes(digest)

        for i in range(n_bits):
            vector[i] += h[i]

    minfeatures = len(hash_digests) / 2
    shash = bitarray(n_bits)
    shash.setall(0)

    for i in range(n_bits):
        shash[i] = vector[i] >= minfeatures

    return shash.tobytes()
