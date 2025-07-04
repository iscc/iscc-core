import pytest
import iscc_core as ic


@pytest.fixture(scope="module")
def idv1():
    timestamp = 1714503123456789  # Some timestamp in microseconds
    server_id = 42  # Server ID between 0-4095
    return ic.gen_iscc_id_v1(timestamp=timestamp, server_id=server_id)["iscc"]


def test_gen_iscc_id_v1_basic():
    """Test basic functionality of gen_iscc_id_v1."""
    # Use a fixed timestamp and server_id for deterministic testing
    timestamp = 1714503123456789  # Some timestamp in microseconds
    server_id = 42  # Server ID between 0-4095

    iscc_id = ic.gen_iscc_id_v1(timestamp=timestamp, server_id=server_id)
    assert iscc_id == {"iscc": "ISCC:MAIGC5KN3I6TCUBK"}
    assert ic.iscc_explain(iscc_id["iscc"]) == "ID-REALM_0-V1-64-1714503123456789-42"
    # Check ISCC-IDv1 is the default implementation:
    iscc_id_default = ic.gen_iscc_id(timestamp=timestamp, server_id=server_id)
    assert iscc_id_default == iscc_id


def test_gen_iscc_id_v1_timestamp_overflow():
    """Test that timestamp overflow raises ValueError."""
    # Create a timestamp that exceeds 52 bits
    overflow_timestamp = 2**52
    server_id = 1

    with pytest.raises(ValueError, match="Timestamp overflow"):
        ic.gen_iscc_id_v1(timestamp=overflow_timestamp, server_id=server_id)


def test_gen_iscc_id_v1_server_id_range():
    """Test with different server IDs within valid range."""
    timestamp = 1714503123456789

    # Test with minimum server_id (0)
    min_id = ic.gen_iscc_id_v1(timestamp=timestamp, server_id=0)
    assert min_id == {"iscc": "ISCC:MAIGC5KN3I6TCUAA"}

    # Test with maximum server_id (4095)
    max_id = ic.gen_iscc_id_v1(timestamp=timestamp, server_id=4095)
    assert max_id == {"iscc": "ISCC:MAIGC5KN3I6TCX77"}

    with pytest.raises(ValueError, match="Server-ID overflow"):
        ic.gen_iscc_id_v1(timestamp=timestamp, server_id=2**12)


def test_gen_iscc_id_v1_different_realms():
    """Test with different realm IDs."""
    timestamp = 1714503123456789
    server_id = 42

    # Test with non-zero realm_id
    with pytest.raises(ValueError, match="Realm-ID overflow"):
        ic.gen_iscc_id_v1(timestamp=timestamp, server_id=server_id, realm_id=1)


def test_gen_iscc_id_v1_structure():
    """Test the internal structure of the ISCC-ID v1."""
    timestamp = 1000000000000000  # Easy to recognize timestamp
    server_id = 123  # Easy to recognize server_id

    iscc_id = ic.gen_iscc_id_v1(timestamp=timestamp, server_id=server_id)

    # Decode the ISCC-ID to verify its structure
    code = ic.Code(iscc_id["iscc"])

    # Check header components
    assert code.maintype == ic.MT.ID
    assert code.subtype == 0  # Default realm_id
    assert code.version == ic.VS.V1
    assert code.length == 64  # 64-bit length

    # Check that the digest contains our timestamp and server_id
    # The digest is 8 bytes (64 bits) where:
    # - First 52 bits (6.5 bytes) are the timestamp
    # - Last 12 bits (1.5 bytes) are the server_id
    digest_int = int.from_bytes(code.hash_bytes, byteorder="big")

    # Extract server_id (last 12 bits)
    extracted_server_id = digest_int & 0xFFF  # 0xFFF = 12 bits of 1s
    assert extracted_server_id == server_id

    # Extract timestamp (first 52 bits)
    extracted_timestamp = digest_int >> 12
    assert extracted_timestamp == timestamp


def test_idv1_validates(idv1):
    assert ic.iscc_validate(idv1)
    assert ic.iscc_validate(idv1, strict=True)


def test_idv1_multiformat(idv1):
    obj = ic.Code.rnd(mt=ic.MT.ID)
