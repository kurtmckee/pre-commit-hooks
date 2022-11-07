from __future__ import annotations

import typing as t

from .common import peek_ahead


file_extensions: set[str] = {
    ".markdown",
    ".md",
}

block_syntax_names: set[str] = {
    "markdown",
    "md",
}


def get_code_blocks(text: str) -> t.Generator[tuple[int, str, str, set[str]], None, None]:
    """Get code blocks from Markdown files.

    Tuples of values are yielded. The tuples have these meanings:

    *   Line number (int)
    *   Block type (like "json")
    *   Code block


    Given a block of Markdown like this::

        # Usage

        Here is an example:

        ```json
        {"example": "1"}
        ```

        Here is another example:

        ```json
        {"example": "2"}
        ```

    This would yield the following tuples::

        (5, "json", '    {"example": "1"}')
        (11, "json", '    {"example": "2"}')

    """

    qa_markers: set[str] = set()

    iterator = peek_ahead(text)
    for block_start_line, current_line, next_line in iterator:
        # Capture qa markers.
        if current_line.startswith("[//]: # (check-code-block:"):
            markers = current_line.partition("check-code-block")[2].strip(":)")
            qa_markers = {marker.strip() for marker in markers.split(",")}
            continue

        # Find fenced code blocks.
        if current_line.startswith("```"):
            # Markdown allows for 3 *or more* backticks,
            # and the closer must be *at least* the same number.
            # The length of the opening fence must be tracked
            # to account for nesting of Markdown syntax blocks.
            block_closer = "`" * (len(current_line) - len(current_line.lstrip("`")))
        elif current_line.startswith("~~~"):
            # As above, the opening fence length must be tracked.
            block_closer = "~" * (len(current_line) - len(current_line.lstrip("~")))
        else:
            # The line is uninteresting.
            continue

        # Identify the block syntax (like "json").
        block_syntax = current_line.lstrip("`~").strip().lower()
        block_start_line += 1

        block_lines = []
        while next_line is not None and not next_line.rstrip().startswith(block_closer):
            _, current_line, next_line = next(iterator)
            block_lines.append(current_line)

        # Consume the next line, which is the block closer.
        next(iterator)

        yield block_start_line, block_syntax, "\n".join(block_lines), qa_markers

        # Reset the qa markers.
        qa_markers = set()
