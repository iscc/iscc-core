"""Build `iscc.json` schema file from iscc_core.schema"""
import iscc_core
from os.path import dirname, abspath, join


HERE = dirname(abspath(__file__))
SCHEMA_PATH = join(HERE, "../iscc_core/iscc.json")


def main():
    """Generate iscc.json schema"""

    with open(SCHEMA_PATH, "wt", encoding="UTF-8") as outf:
        outf.write(iscc_core.ISCC.schema_json(indent=2))


if __name__ == "__main__":
    main()
