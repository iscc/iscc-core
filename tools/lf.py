"""Convert line endings to LF"""
import pathlib

HERE = pathlib.Path(__file__).parent.parent.absolute()

WINDOWS_LINE_ENDING = b"\r\n"
UNIX_LINE_ENDING = b"\n"


def main():
    extensions = {".py", ".toml", ".lock", ".txt", ".md"}
    for fp in HERE.glob("**/*"):
        if fp.suffix in extensions:
            with open(fp, "rb") as infile:
                content = infile.read()
            content = content.replace(WINDOWS_LINE_ENDING, UNIX_LINE_ENDING)
            with open(fp, "wb") as outfile:
                outfile.write(content)
            print(f"lf-converted {fp.as_posix()}")


if __name__ == "__main__":
    main()
