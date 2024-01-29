# -*- coding: utf-8 -*-
import iscc_core as ic


def selftest():
    return ic.conformance_selftest()


if __name__ == "__main__":  # pragma: no cover
    selftest()
