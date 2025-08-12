# -*- coding: utf-8 -*-
"""Build a list of possible base32 encoded ISCC prefixes for validation

IMPORTANT NOTE:
While 3-character prefixes provide full disambiguation (including between V0 and V1 ISCC-IDs),
they cannot be used for general validation because the 3rd character depends on the Length field
in the ISCC header, which varies based on the actual content/hash length.

The PREFIXES constant in constants.py uses 2-character prefixes for validation, which means:
- MA is ambiguous between ID-PRIVATE-V0 and ID-REALM_0-V1
- ME is ambiguous between ID-BITCOIN-V0 and ID-REALM_1-V1

Full disambiguation requires decoding the complete header to check the Version field.
"""
import iscc_core as ic
from collections import defaultdict


def build_valid_prefixes():
    """Generate 2-character prefixes and identify duplicates."""
    prefix_map = defaultdict(list)  # Track which codes map to each prefix

    print("=== Generating 2-character prefixes ===\n")

    # Process all MainTypes
    for mtype in ic.MT:
        if mtype == ic.MT.ID:
            # For ID type, handle both V0 and V1
            # V0 uses ST_ID subtypes
            for stype in ic.ST_ID:
                digest = ic.encode_header(mtype, stype, ic.VS.V0, 0)
                base = ic.encode_base32(digest)
                prefix = base[:2]
                code_type = f"{ic.MT(mtype).name}-{stype.name}-V0"
                prefix_map[prefix].append(code_type)
                print(f"{prefix} -> {code_type}")

            # V1 uses ST_ID_REALM subtypes (REALM_0 and REALM_1)
            for realm in ic.ST_ID_REALM:
                digest = ic.encode_header(mtype, realm, ic.VS.V1, 0)
                base = ic.encode_base32(digest)
                prefix = base[:2]
                code_type = f"{ic.MT(mtype).name}-{realm.name}-V1"
                prefix_map[prefix].append(code_type)
                print(f"{prefix} -> {code_type}")

        elif mtype == ic.MT.META:
            # META uses ST subtypes
            for stype in ic.ST:
                digest = ic.encode_header(mtype, stype, ic.VS.V0, 0)
                base = ic.encode_base32(digest)
                prefix = base[:2]
                code_type = f"{ic.MT(mtype).name}-{stype.name}"
                prefix_map[prefix].append(code_type)
                print(f"{prefix} -> {code_type}")

        elif mtype in (ic.MT.SEMANTIC, ic.MT.CONTENT):
            # SEMANTIC and CONTENT use ST_CC subtypes
            for stype in ic.ST_CC:
                digest = ic.encode_header(mtype, stype, ic.VS.V0, 0)
                base = ic.encode_base32(digest)
                prefix = base[:2]
                code_type = f"{ic.MT(mtype).name}-{stype.name}"
                prefix_map[prefix].append(code_type)
                print(f"{prefix} -> {code_type}")

        elif mtype in (ic.MT.DATA, ic.MT.INSTANCE, ic.MT.FLAKE):
            # DATA, INSTANCE, FLAKE use ST subtypes
            for stype in ic.ST:
                digest = ic.encode_header(mtype, stype, ic.VS.V0, 0)
                base = ic.encode_base32(digest)
                prefix = base[:2]
                code_type = f"{ic.MT(mtype).name}-{stype.name}"
                prefix_map[prefix].append(code_type)
                print(f"{prefix} -> {code_type}")

        elif mtype == ic.MT.ISCC:
            # ISCC uses ST_ISCC subtypes
            for stype in ic.ST_ISCC:
                digest = ic.encode_header(mtype, stype, ic.VS.V0, 0)
                base = ic.encode_base32(digest)
                prefix = base[:2]
                code_type = f"{ic.MT(mtype).name}-{stype.name}"
                prefix_map[prefix].append(code_type)
                print(f"{prefix} -> {code_type}")

    # Report duplicates in 2-character prefixes
    print("\n=== Duplicate 2-character prefixes ===\n")
    duplicates_found = False
    for prefix, types in sorted(prefix_map.items()):
        if len(types) > 1:
            duplicates_found = True
            print(f"{prefix}: {' / '.join(types)}")

    if not duplicates_found:
        print("No duplicate 2-character prefixes found.")

    print(f"\nUnique 2-character prefixes: {sorted(prefix_map.keys())}")
    print(f"Total unique 2-character prefixes: {len(prefix_map)}")

    return sorted(prefix_map.keys())


def build_valid_prefixes_3char():
    """Generate 3-character prefixes and identify duplicates."""
    prefix_map_3 = defaultdict(list)  # Track which codes map to each 3-char prefix

    print("\n=== Generating 3-character prefixes ===\n")

    # Process all MainTypes
    for mtype in ic.MT:
        if mtype == ic.MT.ID:
            # For ID type, handle both V0 and V1
            # V0 uses ST_ID subtypes
            for stype in ic.ST_ID:
                digest = ic.encode_header(mtype, stype, ic.VS.V0, 0)
                base = ic.encode_base32(digest)
                prefix = base[:3] if len(base) >= 3 else base
                code_type = f"{ic.MT(mtype).name}-{stype.name}-V0"
                prefix_map_3[prefix].append(code_type)
                print(f"{prefix} -> {code_type}")

            # V1 uses ST_ID_REALM subtypes (REALM_0 and REALM_1)
            for realm in ic.ST_ID_REALM:
                digest = ic.encode_header(mtype, realm, ic.VS.V1, 0)
                base = ic.encode_base32(digest)
                prefix = base[:3] if len(base) >= 3 else base
                code_type = f"{ic.MT(mtype).name}-{realm.name}-V1"
                prefix_map_3[prefix].append(code_type)
                print(f"{prefix} -> {code_type}")

        elif mtype == ic.MT.META:
            # META uses ST subtypes
            for stype in ic.ST:
                digest = ic.encode_header(mtype, stype, ic.VS.V0, 0)
                base = ic.encode_base32(digest)
                prefix = base[:3] if len(base) >= 3 else base
                code_type = f"{ic.MT(mtype).name}-{stype.name}"
                prefix_map_3[prefix].append(code_type)
                print(f"{prefix} -> {code_type}")

        elif mtype in (ic.MT.SEMANTIC, ic.MT.CONTENT):
            # SEMANTIC and CONTENT use ST_CC subtypes
            for stype in ic.ST_CC:
                digest = ic.encode_header(mtype, stype, ic.VS.V0, 0)
                base = ic.encode_base32(digest)
                prefix = base[:3] if len(base) >= 3 else base
                code_type = f"{ic.MT(mtype).name}-{stype.name}"
                prefix_map_3[prefix].append(code_type)
                print(f"{prefix} -> {code_type}")

        elif mtype in (ic.MT.DATA, ic.MT.INSTANCE, ic.MT.FLAKE):
            # DATA, INSTANCE, FLAKE use ST subtypes
            for stype in ic.ST:
                digest = ic.encode_header(mtype, stype, ic.VS.V0, 0)
                base = ic.encode_base32(digest)
                prefix = base[:3] if len(base) >= 3 else base
                code_type = f"{ic.MT(mtype).name}-{stype.name}"
                prefix_map_3[prefix].append(code_type)
                print(f"{prefix} -> {code_type}")

        elif mtype == ic.MT.ISCC:
            # ISCC uses ST_ISCC subtypes
            for stype in ic.ST_ISCC:
                digest = ic.encode_header(mtype, stype, ic.VS.V0, 0)
                base = ic.encode_base32(digest)
                prefix = base[:3] if len(base) >= 3 else base
                code_type = f"{ic.MT(mtype).name}-{stype.name}"
                prefix_map_3[prefix].append(code_type)
                print(f"{prefix} -> {code_type}")

    # Report duplicates in 3-character prefixes
    print("\n=== Duplicate 3-character prefixes ===\n")
    duplicates_found = False
    for prefix, types in sorted(prefix_map_3.items()):
        if len(types) > 1:
            duplicates_found = True
            print(f"{prefix}: {' / '.join(types)}")

    if not duplicates_found:
        print("No duplicate 3-character prefixes found.")

    print(f"\nUnique 3-character prefixes: {sorted(prefix_map_3.keys())}")
    print(f"Total unique 3-character prefixes: {len(prefix_map_3)}")

    return sorted(prefix_map_3.keys())


if __name__ == "__main__":
    two_char_prefixes = build_valid_prefixes()
    three_char_prefixes = build_valid_prefixes_3char()
