"""Copy README.md to documentation index.md"""
from os.path import abspath, dirname, join


HERE = dirname(abspath(__file__))
SRC = join(HERE, "../README.md")
DST = join(HERE, "../docs/index.md")
CHANGELOG_SRC = join(HERE, "../CHANGELOG.md")
CHANGELOG_DST = join(HERE, "../docs/changelog.md")


def main():
    """Copy root files to documentation site."""
    with open(SRC, "rt", encoding="utf-8") as infile:
        text = infile.read()
    m = "![ISCC Architecture](https://raw.githubusercontent.com/iscc/iscc-core/master/docs/images/iscc-codec-light.png)\n"
    r1 = "![ISCC Architecture](https://raw.githubusercontent.com/iscc/iscc-core/master/docs/images/iscc-codec-light.png#only-light)\n"
    r2 = "![ISCC Architecture](https://raw.githubusercontent.com/iscc/iscc-core/master/docs/images/iscc-codec-dark.png#only-dark)\n"
    text = text.replace(m, r1 + r2)
    with open(DST, "wt", encoding="utf-8", newline="\n") as outf:
        outf.write(text)

    with open(CHANGELOG_SRC, "rt", encoding="utf-8") as infile:
        text = infile.read()
    with open(CHANGELOG_DST, "wt", encoding="utf-8", newline="\n") as outf:
        outf.write(text)


if __name__ == "__main__":
    main()
