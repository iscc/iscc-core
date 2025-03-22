# -*- coding: utf-8 -*-
import pytest
from iscc_core.models import Code
from iscc_core.constants import MT, ST_ISCC


def test_code_rnd_wide():
    """Test that Code.rnd can generate WIDE subtype ISCCs."""
    code = Code.rnd(mt=MT.ISCC, st=ST_ISCC.WIDE)
    assert code.maintype == MT.ISCC
    assert code.subtype == ST_ISCC.WIDE
    assert code.length == 256
    assert code.version == 0
    # Verify the code is in the expected format
    assert code.type_id == "ISCC-WIDE-V0-DI"
