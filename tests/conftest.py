# -*- coding: utf-8 -*-
import io
import pytest

MB1 = 1024 * 1024


def pytest_addoption(parser):
    parser.addoption(
        "--turbo", action="store_true", default=False, help="run extension module tests"
    )


@pytest.fixture
def turbo(request):
    return request.config.getoption("--turbo")


@pytest.fixture(scope="module", name="static_bytes")
def static_bytes_(n: int = MB1, block_size: int = 4) -> bytes:
    """Wraps static_bytes function as a fixture (both can be used)."""
    return static_bytes(n, block_size)


def static_bytes(n: int = MB1, block_size: int = 4) -> bytes:
    """Returns a deterministic inspectable bytesequence with counter bytes for testing.

    Source:
    https://github.com/oconnor663/bao/blob/master/tests/generate_input.py

    :param int n: Number of bytes to generate. (must be a multiple of block_sies)
    :param int block_size: Block size in bytes (blocks begin with a counter)
    :return bytes: deterministic bytestring
    """
    data = io.BytesIO()
    i = 1
    while n > 0:
        ibytes = i.to_bytes(block_size, "little")
        take = min(block_size, n)
        data.write(ibytes[:take])
        n -= take
        i += 1
    return data.getvalue()
