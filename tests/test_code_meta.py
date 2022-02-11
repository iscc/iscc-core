# -*- coding: utf-8 -*-
from textwrap import dedent

import pytest
from iscc_schema import ISCC

import iscc_core


def test_gen_meta_code_title_none():
    m = iscc_core.code_meta.gen_meta_code(None)
    assert m == {
        "iscc": "ISCC:AAA26E2JXH27TING",
        "metahash": "bdyqk6e2jxh27tingubae32rw3teutg6lexe23qisw7gjve6k4qpteyq",
    }
    assert ISCC(**m).iscc == "ISCC:AAA26E2JXH27TING"


def test_gen_meta_code_title_empty_str():
    m = iscc_core.code_meta.gen_meta_code("")
    assert m == {
        "iscc": "ISCC:AAA26E2JXH27TING",
        "metahash": "bdyqk6e2jxh27tingubae32rw3teutg6lexe23qisw7gjve6k4qpteyq",
    }
    assert ISCC(**m).iscc == "ISCC:AAA26E2JXH27TING"


def test_gen_meta_code_title_with_extra():
    empty = {
        "iscc": "ISCC:AAA26E2JXH27TING",
        "metahash": "bdyqk6e2jxh27tingubae32rw3teutg6lexe23qisw7gjve6k4qpteyq",
    }
    m = iscc_core.code_meta.gen_meta_code(None, None)
    assert m == empty
    m = iscc_core.code_meta.gen_meta_code(None, "")
    assert m == empty
    m = iscc_core.code_meta.gen_meta_code("", None)
    assert m == empty
    m = iscc_core.code_meta.gen_meta_code("", "")
    assert m == empty
    assert ISCC(**m).iscc == "ISCC:AAA26E2JXH27TING"


def test_gen_meta_code_description():
    m = iscc_core.code_meta.gen_meta_code("hello", "world")
    assert m == {
        "iscc": "ISCC:AAAWKLHFXNSF7NNE",
        "name": "hello",
        "description": "world",
        "metahash": "bdyqnosmb56tqudeibogyygmf2b25xs7wpg4zux4zcts2v6llqmnj4ja",
    }
    assert ISCC(**m).iscc == "ISCC:AAAWKLHFXNSF7NNE"


def test_gen_meta_code_properties_dict():

    m = iscc_core.code_meta.gen_meta_code("hello", None, {"hello": "metadata"})
    assert m == {
        "iscc": "ISCC:AAAWKLHFXMFCA2OC",
        "metahash": "bdyqay342stvqra22sv77zgt4qdht7nkndrvi6e5edjsxhjl3ufdlbuq",
        "name": "hello",
        "properties": {"hello": "metadata"},
    }
    assert ISCC(**m).iscc == "ISCC:AAAWKLHFXMFCA2OC"


def test_gen_meta_code_properties_bytes():
    m = iscc_core.code_meta.gen_meta_code("", "", b"hello world")
    assert m == {
        "iscc": "ISCC:AAA26E2JXGPXE7WZ",
        "metahash": "bdyqnosmb56tqudeibogyygmf2b25xs7wpg4zux4zcts2v6llqmnj4ja",
        "properties": "aGVsbG8gd29ybGQ=",
    }
    assert ISCC(**m).iscc == "ISCC:AAA26E2JXGPXE7WZ"


def test_gen_meta_code_title_only():
    m = iscc_core.code_meta.gen_meta_code("Hello World")
    assert m == {
        "iscc": "ISCC:AAAWN77F727NXSUS",
        "name": "Hello World",
        "metahash": "bdyqed6bziei6w4j2eilfyrwjbk4pb7mtthesakh5nuuisrfsh72365q",
    }
    assert ISCC(**m).iscc == "ISCC:AAAWN77F727NXSUS"


def test_gen_meta_code_v0_raises():
    with pytest.raises(TypeError):
        iscc_core.code_meta.gen_meta_code_v0("Hello", description=123)


def test_soft_hash_meta_v0_raises():
    with pytest.raises(ValueError):
        iscc_core.code_meta.soft_hash_meta_v0("Hello", extra=123)


def test_hash_meta_v0_empty_title_str():
    m = iscc_core.code_meta.soft_hash_meta_v0("")
    assert len(m) == 32
    assert m.hex() == "af1349b9f5f9a1a6a0404dea36dcc9499bcb25c9adc112b7cc9a93cae41f3262"


def test_hash_meta_v0_empty_title_extra_str():
    m = iscc_core.code_meta.soft_hash_meta_v0("", "")
    assert len(m) == 32
    assert m.hex() == "af1349b9f5f9a1a6a0404dea36dcc9499bcb25c9adc112b7cc9a93cae41f3262"


def test_hash_meta_v0_extra_only():
    m = iscc_core.code_meta.soft_hash_meta_v0("", "Hello")
    assert len(m) == 32
    assert m.hex() == "af1349b9652ce5bbf5f9a1a63fd7018aa0404dea8746265c36dcc949d8a542f4"


def test_hash_meta_v0_interleaved():
    ma = iscc_core.code_meta.soft_hash_meta_v0("")
    mb = iscc_core.code_meta.soft_hash_meta_v0("", "hello")
    assert ma[:4] == mb[:4]
    assert ma[4:8] == mb[8:12]


def test_gen_meta_code_v0_empty_default():
    m = iscc_core.code_meta.gen_meta_code_v0("")
    assert m == dict(
        iscc="ISCC:AAA26E2JXH27TING",
        metahash="bdyqk6e2jxh27tingubae32rw3teutg6lexe23qisw7gjve6k4qpteyq",
    )


def test_gen_meta_code_v0_extra_only_128_bits():
    m = iscc_core.code_meta.gen_meta_code_v0("", "Hello", None, 128)
    assert m == dict(
        iscc="ISCC:AAB26E2JXFSSZZN36X42DJR724AYU",
        description="Hello",
        metahash="bdyqpxqvqkfxoq5cnfe5zqb3zc6fdkcefb7op5fszqv4cyoladnsxsty",
    )


def test_gen_meta_code_v0_interleaved():
    ma = iscc_core.code_meta.gen_meta_code_v0("")
    mb = iscc_core.code_meta.gen_meta_code_v0("", "hello")
    assert ma == {
        "iscc": "ISCC:AAA26E2JXH27TING",
        "metahash": "bdyqk6e2jxh27tingubae32rw3teutg6lexe23qisw7gjve6k4qpteyq",
    }
    assert mb == {
        "iscc": "ISCC:AAA26E2JXFSSZZN3",
        "description": "hello",
        "metahash": "bdyqovdywhwzynauslzcjdrpfrvf3gudo7dau5n4kq3uqrrlcjjtsady",
    }
    assert ma == dict(
        iscc="ISCC:AAA26E2JXH27TING",
        metahash="bdyqk6e2jxh27tingubae32rw3teutg6lexe23qisw7gjve6k4qpteyq",
    )
    assert mb == dict(
        iscc="ISCC:AAA26E2JXFSSZZN3",
        description="hello",
        metahash="bdyqovdywhwzynauslzcjdrpfrvf3gudo7dau5n4kq3uqrrlcjjtsady",
    )
    assert ISCC(**ma).iscc == "ISCC:AAA26E2JXH27TING"
    assert ISCC(**mb).iscc == "ISCC:AAA26E2JXFSSZZN3"


def test_gen_meta_code_v0_properties_raises():
    with pytest.raises(TypeError):
        iscc_core.gen_meta_code_v0("", "", 50, 64)


def test_trim_text():
    multibyte_2 = "ü" * 128
    trimmed = iscc_core.code_meta.text_trim(multibyte_2, 128)
    assert 64 == len(trimmed)
    assert 128 == len(trimmed.encode("utf-8"))

    multibyte_3 = "驩" * 128
    trimmed = iscc_core.code_meta.text_trim(multibyte_3, 128)
    assert 42 == len(trimmed)
    assert 126 == len(trimmed.encode("utf-8"))

    mixed = "Iñtërnâtiônàlizætiøn☃💩" * 6
    trimmed = iscc_core.code_meta.text_trim(mixed, 128)
    assert 85 == len(trimmed)
    assert 128 == len(trimmed.encode("utf-8"))


def test_clean_text_lead_trail():
    assert iscc_core.code_meta.text_clean(" Hello World! ") == "Hello World!"


def test_clean_text_markdowsn():
    text = """

# Document

*Subtitle*


Some Text **text**! Also Iñtërnâtiôn\nàlizætiøn☃💩.

## Subheader

- Maybe even a list
- Item 2
    - Nested
- Unnested

More Text
"""

    assert iscc_core.code_meta.text_clean(text) == (
        "# Document\n"
        "\n"
        "*Subtitle*\n"
        "\n"
        "Some Text **text**! Also Iñtërnâtiôn\n"
        "àlizætiøn☃💩.\n"
        "\n"
        "## Subheader\n"
        "\n"
        "- Maybe even a list\n"
        "- Item 2\n"
        "    - Nested\n"
        "- Unnested\n"
        "\n"
        "More Text"
    )


def test_remove_newlines():
    txt = "   Hello\nWorld!  - How Are you   "
    exp = "Hello World! - How Are you"
    assert iscc_core.code_meta.text_remove_newlines(txt) == exp
