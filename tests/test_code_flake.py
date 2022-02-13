import pytest
import iscc_core as ic


def test_gen_flake_code():
    flake = ic.gen_flake_code()["iscc"]
    assert len(flake) == 21
    assert flake.startswith("ISCC:OAA")


def test_gen_flake_code_v0():
    flake = ic.v0.gen_flake_code_v0()["iscc"]
    assert len(flake) == 21
    assert flake.startswith("ISCC:OAA")


def test_hash_flake_v0():
    assert ic.v0.hash_flake_v0(0).hex().startswith("000000000000")
    ts = 1644789890.9664667
    assert ic.v0.hash_flake_v0(ts).hex().startswith("017ef51dff96")


def test_hash_flake_v0_raises():
    with pytest.raises(ValueError):
        ic.v0.hash_flake_v0(bits=31)
    with pytest.raises(ValueError):
        ic.v0.hash_flake_v0(bits=257)
    with pytest.raises(ValueError):
        ic.v0.hash_flake_v0(bits=65)


def test_flake_to_iso8601():
    assert ic.flake_to_iso8601("ISCC:OAAQC7XVGJIIJU4C") == "2022-02-13T23:27:02.404000"
    assert ic.flake_to_iso8601("OAAQC7XVGJIIJU4C") == "2022-02-13T23:27:02.404000"
