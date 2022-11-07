from __future__ import annotations

import json


block_syntax_names = {
    "json",
    "json-object",
}


def check_syntax(block: str) -> tuple[int, int] | tuple[None, None]:
    """Find a JSON syntax error, if any.

    If any are found, the return value will be a tuple containing:

    *   The line number where the error was found
    *   The column number where the error was found

    """

    try:
        json.loads(block)
    except json.JSONDecodeError as error:
        return error.lineno, error.colno
    return None, None
