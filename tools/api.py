"""Inspect full iscc_core api"""
import inspect
from pathlib import Path
from pprint import pprint
import iscc_core
import imp
import os
import ast
from os.path import dirname, join


MODULE_EXTENSIONS = (".py",)
PKG_DIR = dirname(iscc_core.__file__)


def package_contents(package_name):
    file, pathname, description = imp.find_module(package_name)
    if file:
        raise ImportError("Not a package: %r", package_name)
    # Use a set because some may be both source and compiled.
    return set(
        [
            join(PKG_DIR, module)
            for module in os.listdir(pathname)
            if module.endswith(MODULE_EXTENSIONS)
        ]
    )


def top_level_functions(body):
    return (f for f in body if isinstance(f, ast.FunctionDef))


def parse_ast(filename):
    with open(filename, "rt") as file:
        return ast.parse(file.read(), filename=filename)


def iscc_core_api() -> str:
    module_file_paths = package_contents("iscc_core")
    functions = []
    for mf in module_file_paths:
        module_name = Path(mf).stem
        tree = parse_ast(mf)
        for func in top_level_functions(tree.body):
            functions.append(f"{func.name}")
    return sorted(functions)


def iscc_core_top_members() -> str:
    members = []
    for name, obj in inspect.getmembers(iscc_core):
        if not name.startswith("__"):
            members.append(name)
    return sorted(members)


if __name__ == "__main__":
    print("################### TOP LEVEL API ##################")
    pprint(iscc_core_top_members())
    print("################### CORE API ##################")
    pprint(iscc_core_api())
