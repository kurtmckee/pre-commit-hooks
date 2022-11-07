from __future__ import annotations

import ast


block_syntax_names = {
    "py",
    "py3",
    "python",
    "python3",
}


def check_syntax(block: str) -> tuple[int, int] | tuple[None, None]:
    """Find a Python syntax error, if any.

    If any are found, the return value will be a tuple containing:

    *   The line number where the error was found
    *   The column number where the error was found

    """

    try:
        ast.parse(block)
    except SyntaxError as error:
        return error.lineno, error.offset
    return None, None
