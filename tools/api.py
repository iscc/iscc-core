"""Inspect full iscc_core api"""

import inspect
from pprint import pprint
import iscc_core
import importlib.util
import os
import ast
from os.path import dirname, join


MODULE_EXTENSIONS = (".py",)
PKG_DIR = dirname(iscc_core.__file__)


def package_contents(package_name):
    spec = importlib.util.find_spec(package_name)
    if spec is None:
        raise ImportError("Package not found: %r" % package_name)

    if spec.submodule_search_locations is None:
        raise ImportError("Not a package: %r" % package_name)

    package_path = spec.submodule_search_locations[0]

    return set(
        [
            os.path.join(package_path, module)
            for module in os.listdir(package_path)
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
        if not mf.endswith(".py"):
            continue
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
