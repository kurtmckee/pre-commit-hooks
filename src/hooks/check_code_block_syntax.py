from __future__ import annotations

import pathlib
import sys
import typing as t

from . import markdown
from . import restructuredtext
from . import asciidoc
from .syntax import json_
from .syntax import python_


RC_SUCCESS: t.Final[t.Literal[0]] = 0
RC_FAILURE: t.Final[t.Literal[1]] = 1


def check_block(path: pathlib.Path, text: str) -> t.Literal[0, 1]:
    if path.suffix in restructuredtext.file_extensions:
        get_code_blocks = restructuredtext.get_code_blocks
    elif path.suffix in markdown.file_extensions:
        get_code_blocks = markdown.get_code_blocks
    elif path.suffix in asciidoc.file_extensions:
        get_code_blocks = asciidoc.get_code_blocks
    else:
        # Unsupported file extension.
        raise NotImplementedError(f"{path.suffix} is not a recognized file extension")

    return_code: t.Literal[0, 1] = RC_SUCCESS
    for block_start_line, block_type, block, noqa in get_code_blocks(text):
        line = column = None
        if "syntax" in noqa:
            continue
        if block_type == "json":
            line, column = json_.check_syntax(block)
        elif block_type == "python":
            line, column = python_.check_syntax(block)
        if (line, column) == (None, None):
            continue

        return_code = RC_FAILURE
        line += block_start_line
        print(f"{path} has a {block_type} syntax error at line {line}, column {column}")

    return return_code


def main() -> t.Literal[0, 1]:
    try:
        path = pathlib.Path(sys.argv[1])
    except KeyError:
        print("No path provided")
        return RC_FAILURE

    if path.suffix not in {".rst"}:
        print(f"{path} must have a known suffix (got {path.suffix})")
        return RC_FAILURE

    if not path.is_file():
        print(f"{path} does not exist, or is not a file")
        return RC_FAILURE

    try:
        text = path.read_text()
    except UnicodeDecodeError:
        print(f"{path} is not UTF-8 encoded")
        return RC_FAILURE

    try:
        return check_block(path, text)
    except NotImplementedError:
        return RC_SUCCESS


if __name__ == "__main__":
    sys.exit(main())
