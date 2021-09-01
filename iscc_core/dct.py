# -*- coding: utf-8 -*-
import math
from collections.abc import Sequence


def dct(v: Sequence[float]):
    """
    Discrete cosine transform by Project Nayuki. (MIT License)
    See: https://www.nayuki.io/page/fast-discrete-cosine-transform-algorithms
    """

    n = len(v)
    if n == 1:
        return list(v)
    elif n == 0 or n % 2 != 0:
        raise ValueError()
    else:
        half = n // 2
        alpha = [(v[i] + v[-(i + 1)]) for i in range(half)]
        beta = [
            (v[i] - v[-(i + 1)]) / (math.cos((i + 0.5) * math.pi / n) * 2.0)
            for i in range(half)
        ]
        alpha = dct(alpha)
        beta = dct(beta)
        result = []
        for i in range(half - 1):
            result.append(alpha[i])
            result.append(beta[i] + beta[i + 1])
        result.append(alpha[-1])
        result.append(beta[-1])
        return result
