# -*- coding: utf-8 -*-
import pytest
import iscc_core as ic


def test_gen_meta_code_name_none():
    with pytest.raises(ValueError):
        ic.gen_meta_code_v0(None)


def test_gen_meta_code_name_empty_str():
    with pytest.raises(ValueError):
        ic.gen_meta_code_v0(" ")


def test_gen_meta_code_name_only():
    result = ic.gen_meta_code_v0("Hello  World")
    assert result == {
        "iscc": "ISCC:AAAWN77F727NXSUS",
        "name": "Hello World",
        "metahash": "1e2041f8394111eb713a22165c46c90ab8f0fd9399c92028fd6d288944b23ff5bf76",
    }


def test_gen_meta_code_name_and_desc():
    result = ic.gen_meta_code_v0("Hello  World", "# Some\n\n\n description")
    assert result == {
        "iscc": "ISCC:AAAWN77F72MBZZK3",
        "name": "Hello World",
        "description": "# Some\n\n description",
        "metahash": "1e20bd06bd79a3df82b163e346e5a477062aed41c2a9cf1e5812cf8947e2e3555a38",
    }


def test_gen_meta_code_meta_dict():
    m = ic.gen_meta_code_v0("hello", None, {"hello": "metadata"})
    assert m == {
        "iscc": "ISCC:AAAWKLHFXMFCA2OC",
        "name": "hello",
        "meta": "data:application/json;base64,eyJoZWxsbyI6Im1ldGFkYXRhIn0=",
        "metahash": "1e200c6f9a94eb08835a957ffc9a7c80cf3fb54d1c6a8f13a41a6573a57ba146b0d2",
    }


def test_gen_meta_code_meta_bytes():
    with pytest.raises(TypeError):
        ic.gen_meta_code_v0("Hello", "", b"hello world")


def test_gen_meta_code_meta_non_url_str():
    with pytest.raises(AttributeError):
        ic.gen_meta_code_v0("Hello", "", "hello world")


def test_gen_meta_code_v0_raises():
    with pytest.raises(TypeError):
        ic.gen_meta_code_v0("Hello", description=123)


def test_soft_hash_meta_v0_raises():
    with pytest.raises(ValueError):
        ic.soft_hash_meta_v0("Hello", extra=123)


def test_hash_meta_v0_empty_title_str():
    m = ic.soft_hash_meta_v0("")
    assert len(m) == 32
    assert m.hex() == "af1349b9f5f9a1a6a0404dea36dcc9499bcb25c9adc112b7cc9a93cae41f3262"


def test_hash_meta_v0_empty_title_extra_str():
    m = ic.soft_hash_meta_v0("", "")
    assert len(m) == 32
    assert m.hex() == "af1349b9f5f9a1a6a0404dea36dcc9499bcb25c9adc112b7cc9a93cae41f3262"


def test_hash_meta_v0_extra_only():
    m = ic.soft_hash_meta_v0("", "Hello")
    assert len(m) == 32
    assert m.hex() == "af1349b9652ce5bbf5f9a1a63fd7018aa0404dea8746265c36dcc949d8a542f4"


def test_hash_meta_v0_interleaved():
    ma = ic.soft_hash_meta_v0("")
    mb = ic.soft_hash_meta_v0("", "hello")
    assert ma[:4] == mb[:4]
    assert ma[4:8] == mb[8:12]


def test_gen_meta_code_v0_interleaved():
    ma = ic.gen_meta_code_v0("Hello")
    mb = ic.gen_meta_code_v0("Hello", "World")
    assert ma == {
        "iscc": "ISCC:AAAWKLHFXM75OAMK",
        "metahash": "1e20fbc2b0516ee8744d293b980779178a3508850fdcfe965985782c39601b65794f",
        "name": "Hello",
    }
    assert mb == {
        "description": "World",
        "iscc": "ISCC:AAAWKLHFXNSF7NNE",
        "metahash": "1e2041f8394111eb713a22165c46c90ab8f0fd9399c92028fd6d288944b23ff5bf76",
        "name": "Hello",
    }


def test_gen_meta_code_v0_metadata_raises():
    with pytest.raises(TypeError):
        ic.gen_meta_code_v0("Hello", "", 50, 64)


def test_trim_text():
    multibyte_2 = "ü" * 128
    trimmed = ic.text_trim(multibyte_2, 128)
    assert 64 == len(trimmed)
    assert 128 == len(trimmed.encode("utf-8"))

    multibyte_3 = "驩" * 128
    trimmed = ic.text_trim(multibyte_3, 128)
    assert 42 == len(trimmed)
    assert 126 == len(trimmed.encode("utf-8"))

    mixed = "Iñtërnâtiônàlizætiøn☃💩" * 6
    trimmed = ic.text_trim(mixed, 128)
    assert 85 == len(trimmed)
    assert 128 == len(trimmed.encode("utf-8"))


def test_clean_text_lead_trail():
    assert ic.text_clean(" Hello World! ") == "Hello World!"


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

    assert ic.text_clean(text) == (
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
    assert ic.text_remove_newlines(txt) == exp
