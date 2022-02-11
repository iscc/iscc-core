"""Copy README.md to documentation index.md"""
from os.path import abspath, dirname, join
import shutil


HERE = dirname(abspath(__file__))
SRC = join(HERE, "../README.md")
DST = join(HERE, "../docs/index.md")


def main():
    """Copy README.md to documentation index.md"""
    with open(SRC, "rt", encoding="utf-8") as infile:
        text = infile.read()
    m = "![ISCC Architecture](https://raw.githubusercontent.com/iscc/iscc-core/master/docs/images/iscc-codec-light.png)\n"
    r1 = "![ISCC Architecture](https://raw.githubusercontent.com/iscc/iscc-core/master/docs/images/iscc-codec-light.png#only-light)\n"
    r2 = "![ISCC Architecture](https://raw.githubusercontent.com/iscc/iscc-core/master/docs/images/iscc-codec-dark.png#only-dark)\n"
    text = text.replace(m, r1 + r2)
    with open(DST, "wt", encoding="utf-8", newline="\n") as outf:
        outf.write(text)


if __name__ == "__main__":
    main()
