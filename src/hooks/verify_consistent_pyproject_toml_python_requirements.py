# This file is part of a pre-commit hook repository.
# Copyright 2024 Kurt McKee <contactme@kurtmckee.org>
# SPDX-License-Identifier: MIT

from __future__ import annotations

import pathlib
import sys
import tomllib
import typing as t

RC_SUCCESS: t.Final[t.Literal[0]] = 0
RC_FAILURE: t.Final[t.Literal[1]] = 1


def main() -> t.Literal[0, 1]:
    """Verify all ``pyproject.toml`` files share the same Python version requirement."""

    rc = RC_SUCCESS

    # Get the authoritative Python requirement value from `/pyproject.toml`.
    root = pathlib.Path("pyproject.toml")
    try:
        root_requirement = _get_toml_python_requirement(root)
    except AssertionError as error:
        print(error.args[0])
        return RC_FAILURE

    # Compare versions.
    try:
        for path in _get_pyproject_toml_files():
            if path == root:
                continue
            try:
                requirement = _get_toml_python_requirement(path)
            except AssertionError as error:
                print(error.args[0])
                rc = RC_FAILURE
                continue
            if requirement != root_requirement:
                print(f"'{path}' does not have the same Python requirement as '{root}'")
                rc = RC_FAILURE
    except AssertionError as error:
        print(error.args[0])
        rc = RC_FAILURE

    return rc


def _get_toml_python_requirement(path: pathlib.Path) -> str:
    """Load a TOML file and return its Python requirement string."""

    if not path.is_file():
        raise AssertionError(f"'{path}' does not exist")
    try:
        standard_config = tomllib.loads(path.read_text(encoding="utf-8"))
        python_requirement = standard_config["tool"]["poetry"]["dependencies"]["python"]
    except UnicodeDecodeError:
        raise AssertionError(f"'{path}' could not be decoded as UTF-8")
    except tomllib.TOMLDecodeError:
        raise AssertionError(f"'{path}' could not be parsed as TOML")
    except KeyError:
        message = f"'{path}' does not contain a 'tool.poetry.dependencies.python' key"
        raise AssertionError(message)
    if not isinstance(python_requirement, str):
        message = f"'{path}' has a non-string 'tool.poetry.dependencies.python' value"
        raise AssertionError(message)

    return python_requirement


def _get_pyproject_toml_files() -> t.Generator[pathlib.Path, None, None]:
    """Find ``pyproject.toml`` files in specified paths."""

    for argument in sys.argv[1:]:
        path = pathlib.Path(argument)
        if path.is_file():
            yield path
        elif path.is_dir():
            yield from path.rglob("**/pyproject.toml")
        else:
            raise AssertionError(f"'{argument}' must be a file or directory")


if __name__ == "__main__":
    sys.exit(main())
