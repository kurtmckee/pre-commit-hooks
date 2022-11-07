from __future__ import annotations

import typing as t


supported_qa_markers: set[str] = {
    "ignore-syntax",
    "noqa",  # Disable all checks
}


def peek_ahead(text: str) -> t.Generator[tuple[int, str, str | None], None, None]:
    iterator = iter(text.splitlines())
    try:
        current_line = next(iterator)
    except StopIteration:
        return
    line_number = 0
    for line_number, next_line in enumerate(iterator):
        yield line_number, current_line, next_line
        current_line = next_line
    yield line_number, current_line, None
