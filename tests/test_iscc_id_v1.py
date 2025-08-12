import pytest
import iscc_core as ic


@pytest.fixture(scope="module")
def idv1():
    timestamp = 1714503123456789  # Some timestamp in microseconds
    hub_id = 42  # HUB ID between 0-4095
    return ic.gen_iscc_id_v1(timestamp=timestamp, hub_id=hub_id, realm_id=0)["iscc"]


def test_gen_iscc_id_v1_basic():
    """Test basic functionality of gen_iscc_id_v1."""
    # Use a fixed timestamp and hub_id for deterministic testing
    timestamp = 1714503123456789  # Some timestamp in microseconds
    hub_id = 42  # HUB ID between 0-4095

    # Test with realm_id=0 (test network)
    iscc_id = ic.gen_iscc_id_v1(timestamp=timestamp, hub_id=hub_id, realm_id=0)
    assert iscc_id == {"iscc": "ISCC:MAIGC5KN3I6TCUBK"}
    assert ic.iscc_explain(iscc_id["iscc"]) == "ID-REALM_0-V1-64-1714503123456789-42"

    # Test with realm_id=1 (operational network) - now the default
    iscc_id_default = ic.gen_iscc_id(timestamp=timestamp, hub_id=hub_id)
    # Since realm_id=1 is now default, the ISCC will be different
    # We'll need to check that it's using realm_id=1 correctly


def test_gen_iscc_id_v1_timestamp_overflow():
    """Test that timestamp overflow raises ValueError."""
    # Create a timestamp that exceeds 52 bits
    overflow_timestamp = 2**52
    hub_id = 1

    with pytest.raises(ValueError, match="Timestamp overflow"):
        ic.gen_iscc_id_v1(timestamp=overflow_timestamp, hub_id=hub_id)


def test_gen_iscc_id_v1_hub_id_range():
    """Test with different HUB IDs within valid range."""
    timestamp = 1714503123456789

    # Test with minimum hub_id (0) and realm_id=0 (test network)
    min_id = ic.gen_iscc_id_v1(timestamp=timestamp, hub_id=0, realm_id=0)
    assert min_id == {"iscc": "ISCC:MAIGC5KN3I6TCUAA"}

    # Test with maximum hub_id (4095) and realm_id=0 (test network)
    max_id = ic.gen_iscc_id_v1(timestamp=timestamp, hub_id=4095, realm_id=0)
    assert max_id == {"iscc": "ISCC:MAIGC5KN3I6TCX77"}

    with pytest.raises(ValueError, match="HUB-ID overflow"):
        ic.gen_iscc_id_v1(timestamp=timestamp, hub_id=2**12)


def test_gen_iscc_id_v1_different_realms():
    """Test with different realm IDs."""
    timestamp = 1714503123456789
    hub_id = 42

    # Test with realm_id=0 (test network)
    test_id = ic.gen_iscc_id_v1(timestamp=timestamp, hub_id=hub_id, realm_id=0)
    assert test_id == {"iscc": "ISCC:MAIGC5KN3I6TCUBK"}

    # Test with realm_id=1 (operational network)
    operational_id = ic.gen_iscc_id_v1(timestamp=timestamp, hub_id=hub_id, realm_id=1)
    # The ISCC will be different due to different realm_id in the header
    assert operational_id["iscc"] != test_id["iscc"]

    # Test with invalid realm_id
    with pytest.raises(ValueError, match="Realm-ID must be 0 \(test\) or 1 \(operational\)"):
        ic.gen_iscc_id_v1(timestamp=timestamp, hub_id=hub_id, realm_id=2)


def test_gen_iscc_id_v1_structure():
    """Test the internal structure of the ISCC-ID v1."""
    timestamp = 1000000000000000  # Easy to recognize timestamp
    hub_id = 123  # Easy to recognize hub_id

    iscc_id = ic.gen_iscc_id_v1(timestamp=timestamp, hub_id=hub_id, realm_id=0)

    # Decode the ISCC-ID to verify its structure
    code = ic.Code(iscc_id["iscc"])

    # Check header components
    assert code.maintype == ic.MT.ID
    assert code.subtype == 0  # realm_id=0 (test network)
    assert code.version == ic.VS.V1
    assert code.length == 64  # 64-bit length

    # Check that the digest contains our timestamp and hub_id
    # The digest is 8 bytes (64 bits) where:
    # - First 52 bits (6.5 bytes) are the timestamp
    # - Last 12 bits (1.5 bytes) are the hub_id
    digest_int = int.from_bytes(code.hash_bytes, byteorder="big")

    # Extract hub_id (last 12 bits)
    extracted_hub_id = digest_int & 0xFFF  # 0xFFF = 12 bits of 1s
    assert extracted_hub_id == hub_id

    # Extract timestamp (first 52 bits)
    extracted_timestamp = digest_int >> 12
    assert extracted_timestamp == timestamp


def test_idv1_validates(idv1):
    assert ic.iscc_validate(idv1)
    assert ic.iscc_validate(idv1, strict=True)


def test_idv1_multiformat(idv1):
    obj = ic.Code.rnd(mt=ic.MT.ID)
