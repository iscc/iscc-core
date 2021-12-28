"""Build docs/context/<v>.json JSON-LD file from iscc_core.schema"""
import iscc_core
from os.path import dirname, abspath, join
import json

HERE = dirname(abspath(__file__))
SCHEMA_PATH = join(HERE, f"../docs/context/{iscc_core.__version__}.json")


def main():
    """Generate iscc.json schema"""

    with open(SCHEMA_PATH, "wt", encoding="UTF-8") as outf:
        outf.write(json.dumps(iscc_core.ISCC.jsonld_context(), indent=4))


if __name__ == "__main__":
    main()
