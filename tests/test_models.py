# -*- coding: utf-8 -*-
from iscc_core.models import Code
from iscc_core.constants import MT, ST_ISCC, ST_ID_REALM, VS


def test_code_rnd_wide():
    """Test that Code.rnd can generate WIDE subtype ISCCs."""
    code = Code.rnd(mt=MT.ISCC, st=ST_ISCC.WIDE)
    assert code.maintype == MT.ISCC
    assert code.subtype == ST_ISCC.WIDE
    assert code.length == 256
    assert code.version == 0
    # Verify the code is in the expected format
    assert code.type_id == "ISCC-WIDE-V0-DI"


def test_code_wide_encoding_decoding():
    """Test that WIDE ISCCs can be properly encoded and decoded."""
    # Create a WIDE ISCC
    code1 = Code.rnd(mt=MT.ISCC, st=ST_ISCC.WIDE)

    # Test that encoding and re-decoding preserves properties
    encoded = code1.code
    code2 = Code(encoded)

    assert code2.maintype == MT.ISCC
    assert code2.subtype == ST_ISCC.WIDE
    assert code2.length == 256
    assert code2.version == 0
    assert code2.type_id == "ISCC-WIDE-V0-DI"

    # Ensure they're equal
    assert code1 == code2


def test_code_wide_properties():
    """Test various Code properties with WIDE ISCCs."""
    code = Code.rnd(mt=MT.ISCC, st=ST_ISCC.WIDE)

    # Test hash_* properties
    assert len(code.hash_bytes) == 32  # 256 bits = 32 bytes
    assert len(code.hash_hex) == 64  # 32 bytes = 64 hex chars
    assert len(code.hash_bits) == 256  # 256 bits
    assert len(code.hash_ints) == 256  # 256 bits

    # Test the explanation contains the right type info
    assert "ISCC-WIDE-V0-DI" in code.explain

    # Test URI representation
    assert code.uri.startswith("ISCC:")


def test_code_wide_equality():
    """Test equality and hash operations with WIDE ISCCs."""
    code1 = Code.rnd(mt=MT.ISCC, st=ST_ISCC.WIDE)

    # Test equality with same code
    code2 = Code(code1.code)
    assert code1 == code2
    assert hash(code1) == hash(code2)

    # Create a different WIDE ISCC and ensure inequality
    code3 = Code.rnd(mt=MT.ISCC, st=ST_ISCC.WIDE)
    assert code1 != code3

    # Test code can be used in a set
    code_set = {code1, code2, code3}
    assert len(code_set) == 2  # code1 and code2 are equal, so only 2 unique codes


def test_code_wide_multiformat():
    """Test multiformat representations of WIDE ISCCs."""
    code = Code.rnd(mt=MT.ISCC, st=ST_ISCC.WIDE)

    # Test multiformat encodings
    assert code.mf_base16.startswith("f")
    assert code.mf_base32.startswith("b")
    assert code.mf_base32hex.startswith("v")
    assert code.mf_base58btc.startswith("z")
    assert code.mf_base64url.startswith("u")

    # Verify that multicodec prefix is included
    assert len(code.mc_bytes) == len(code.bytes) + 2
    assert code.mc_bytes[:2] == b"\xcc\x01"


def test_code_iscc_idv1():
    """Test Code class compatibility with ISCC-IDv1."""
    # Create test data
    timestamp = 1647312000000000  # 2022-03-15 12:00:00 UTC in microseconds
    server_id = 42

    # Generate an ISCC-IDv1 using the generator function
    from iscc_core.iscc_id import gen_iscc_id_v1

    iscc_id = gen_iscc_id_v1(timestamp, server_id)["iscc"]

    # Initialize Code object from ISCC-IDv1 string
    code = Code(iscc_id)

    # Test basic properties
    assert code.maintype == MT.ID
    assert code.subtype == ST_ID_REALM.REALM_0
    assert code.version == VS.V1
    assert code.length == 64

    # Test type identification
    assert code.type_id == "ID-REALM_0-V1-64"
    assert "ID-REALM_0-V1-64" in code.explain
    assert f"{timestamp}-{server_id}" in code.explain

    # Test hash properties contain correct data
    # Body should be 8 bytes: 52 bits timestamp + 12 bits server_id
    assert len(code.hash_bytes) == 8
    body_int = int.from_bytes(code.hash_bytes, byteorder="big")
    decoded_server_id = body_int & 0xFFF
    decoded_timestamp = body_int >> 12
    assert decoded_timestamp == timestamp
    assert decoded_server_id == server_id

    # Test string representations
    assert code.uri.startswith("ISCC:")
    assert code == Code(code.code)  # Test round-trip through string encoding
