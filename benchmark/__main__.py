# -*- coding: utf-8 -*-
import sys
from . import bench_code_data


def main():
    if len(sys.argv) < 2:
        print("Usage: python -m benchmark <command> [args...]")
        print("\nAvailable commands:")
        print("  datacode <filepath>  - Benchmark data code generation")
        return

    command = sys.argv[1]
    if command == "datacode":
        bench_code_data.main()
    else:
        print(f"Unknown command: {command}")
        print("Use 'python -m benchmark' to see available commands")


if __name__ == "__main__":
    main()
