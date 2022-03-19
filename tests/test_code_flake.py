import pytest
import iscc_core as ic

TS = 1644830125.1892536


def test_gen_flake_code():
    flake = ic.gen_flake_code()["iscc"]
    assert len(flake) == 21
    assert flake.startswith("ISCC:OAA")


def test_gen_flake_code_v0():
    flake = ic.v0.gen_flake_code_v0()["iscc"]
    assert len(flake) == 21
    assert flake.startswith("ISCC:OAA")


def test_uid_flake_v0():
    assert ic.v0.uid_flake_v0(0).hex().startswith("000000000000")
    ts = 1644789890.9664667
    assert ic.v0.uid_flake_v0(ts).hex().startswith("017ef51dff96")


def test_uid_flake_v0_raises():
    with pytest.raises(ValueError):
        ic.v0.uid_flake_v0(bits=31)
    with pytest.raises(ValueError):
        ic.v0.uid_flake_v0(bits=257)
    with pytest.raises(ValueError):
        ic.v0.uid_flake_v0(bits=65)


def test_Flake_init():
    flake = ic.Flake()
    assert isinstance(flake, ic.Flake)


def test_Flake_iscc():
    flake = ic.Flake(ts=TS)
    assert flake.iscc.startswith("ISCC:OAAQC7XXQPWI")


def test_Flake_repr():
    flake = ic.Flake(ts=TS)
    assert repr(flake).startswith('Flake("05VFF0VC')


def test_Flake_str():
    flake = ic.Flake(ts=TS)
    assert str(flake) == flake.string
    assert flake.string.startswith("05VFF0VCG")


def test_Flake_int():
    flake = ic.Flake(ts=TS)
    assert isinstance(flake.int, int)
    assert str(flake.int).startswith("107795587084")


def test_Flake_time():
    flake = ic.Flake(ts=TS)
    assert flake.time == "2022-02-14T09:15:25.189"


def test_Flake_from_int():
    flake = ic.Flake()
    assert flake == ic.Flake.from_int(flake.int)


def test_Flake_from_str():
    flake = ic.Flake()
    assert flake == ic.Flake.from_string(flake.string)


def test_Flake_hashable():
    assert {ic.Flake()}


def test_Flake_ordered():
    f1 = ic.Flake()
    f2 = ic.Flake()
    assert f1 < f2
    assert f2 > f1
