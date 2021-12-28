"""Build docs/context/<v>.json JSON-LD file from iscc_core.schema"""
import iscc_core
from os.path import dirname, abspath, join
import json

HERE = dirname(abspath(__file__))
SCHEMA_PATH = join(HERE, f"../docs/context/{iscc_core.__version__}.json")
DOC_PATH = join(HERE, f"../docs/context/{iscc_core.__version__}/index.md")


def main():
    """Generate `docs/context/<0.0.0>.json` schema and index.md"""

    with open(SCHEMA_PATH, "wt", encoding="UTF-8") as outf:
        outf.write(json.dumps(iscc_core.ISCC.jsonld_context(), indent=4))

    doc = f"""---
hide:
  - navigation
---

# **ISCC** - Metadata Vocabulary (v{iscc_core.__version__})

"""

    for prop, fields in iscc_core.ISCC.schema()["properties"].items():
        print(prop, fields)
        print()
        doc += f"## {prop}\n\n"
        doc += '!!! term ""\n'
        doc += f"    {fields['description']}\n\n"

    with open(DOC_PATH, "wt", encoding="UTF-8") as outf:
        outf.write(doc)


if __name__ == "__main__":
    main()
