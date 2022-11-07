from __future__ import annotations

import typing as t

from .common import peek_ahead


file_extensions: set[str] = {
    ".rst",
}

block_syntax_names: set[str] = {
    "rest",
    "restructuredtext",
    "rst",
}


def consume_lines_up_to_content(
    iterator: t.Generator[tuple[int, str, str]], allow_options: bool = True
) -> tuple[int, int]:
    """Consume options (like ":caption:") and blank lines leading up to content.

    For code blocks, *allow_options* should be True.
    For literal blocks, *allow_options* should be False.

    The return value is tuple of integers:

    *   The line number - 1 where the content in the code block begins
        (or the most recent line of the file, if the code block is malformed)
    *   The indent level of the code block (or 0, if the code block is malformed)

    When the loop exits (assuming the code block is well-formed),
    the iterator is primed to begin returning content lines.
    """

    options_indent = 0
    while True:
        block_start_line, current_line, next_line = next(iterator)

        # If the end of the file has been reached, the code block is malformed.
        if next_line is None:
            return block_start_line, 0

        # If options are found, they set the indent level.
        if allow_options and current_line.lstrip().startswith(":"):
            options_indent = len(current_line) - len(current_line.lstrip())

        # If the current line is blank and the next line is not,
        # the next line is either code content or the code block is malformed.
        # Exit either way.
        elif current_line.strip() == "" and next_line.strip():
            content_indent = len(next_line) - len(next_line.lstrip())
            if not content_indent or content_indent < options_indent:
                return block_start_line, 0
            return block_start_line, options_indent or content_indent


def get_code_blocks(text: str) -> t.Generator[tuple[int, str, str, set[str]], None, None]:
    """Get code blocks from Restructured Text files.

    Tuples of values are yielded. The tuples have these meanings:

    *   Line number (int)
    *   Block type (like "json")
    *   Code block


    Given a block of Restructured Text like this::

        Usage
        =====

        Here is an example:

        ..  code-block:: json
            :caption: Example 1

            {"example": "1"}

        Here is another example:

        ..  highlight:: json

        ::

            {"example": "2"}

    This would yield the following tuples::

        (8, "json", '    {"example": "1"}\n')
        (16, "json", '    {"example": "2"}\n')

    """

    block_syntax = ""
    highlight_syntax = ""
    qa_markers: set[str] = set()

    iterator = peek_ahead(text)
    for block_start_line, current_line, next_line in iterator:
        if current_line.startswith(".. "):
            # Highlight directives set the syntax for all code blocks that follow.
            # Restructured Text allows multiple highlight directives.
            if current_line[3:].lstrip().startswith("highlight::"):
                _, _, highlight_syntax = current_line.partition("highlight::")
                highlight_syntax = highlight_syntax.strip().lower()
                continue

            # Capture check-code-block markers.
            # These are comments, not directives, so there is only one colon.
            if current_line[3:].lstrip().startswith("check-code-block: "):
                qa_markers = {
                    i.strip()
                    for i in current_line.partition("check-code-block: ")[2].split(",")
                }
                continue

            if current_line[3:].lstrip().startswith(("code-block::", "sourcecode::")):
                # This is a code-block directive.
                # Identify the block syntax (like "json").
                _, _, block_syntax = current_line.partition("::")
                block_syntax = block_syntax.strip().lower()

                # Discard options (like ":caption:") and leading blank lines.
                block_start_line, indent = consume_lines_up_to_content(iterator)

                # Deliberately fall through instead of continuing.

            else:
                # This isn't an interesting line.
                continue

        elif current_line.endswith("::") and next_line.strip() == "":
            # This is a literal block.
            # Consume all blank lines leading up to the code content.
            block_start_line, indent = consume_lines_up_to_content(iterator, allow_options=False)

        else:
            # This is not a code-block nor a literal block. Ignore this line.
            continue

        # If the indent level is 0, this indicates an RST syntax error.
        # This is currently not reported by this tool.
        if not indent:
            block_syntax = ""
            qa_markers = set()
            continue

        # The code content has been primed to start on the next line.
        block_start_line += 1

        # Collect the code content.
        # Stop when the end of the file is reached,
        # or when the indentation level of the next line decreases.
        block_lines = []
        while True:
            _, current_line, next_line = next(iterator)
            block_lines.append(current_line[indent:])
            if next_line is None or (next_line.strip() and len(next_line) - len(next_line.lstrip()) < indent):
                break

        # Remove blank trailing lines from the block.
        while block_lines and not block_lines[-1].strip():
            block_lines.pop()

        yield block_start_line, block_syntax or highlight_syntax, "\n".join(block_lines), qa_markers

        # Reset.
        block_syntax = ""
        qa_markers = set()
