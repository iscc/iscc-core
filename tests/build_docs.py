"""Copy README.md to documentation index.md"""
from os.path import abspath, dirname, join
import shutil


HERE = dirname(abspath(__file__))
SRC = join(HERE, "../README.md")
DST = join(HERE, "../docs/index.md")


def main():
    """Copy README.md to documentation index.md"""
    shutil.copyfile(
        SRC,
        DST,
    )


if __name__ == "__main__":
    main()
