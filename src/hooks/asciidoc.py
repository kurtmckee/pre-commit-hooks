from __future__ import annotations

import typing as t

from .common import peek_ahead


file_extensions: set[str] = {
    ".adoc",
    ".asciidoc",
}

block_syntax_names: set[str] = {
    "adoc",
    "asciidoc",
}


def get_code_blocks(text: str) -> t.Generator[tuple[int, str, str, set[str]], None, None]:
    """Get code blocks from AsciiDoc files.

    Tuples of values are yielded. The tuples have these meanings:

    *   Line number (int)
    *   Block type (like "json")
    *   Code block


    Given a block of AsciiDoc like this::

        = Usage
        :source-language: json

        Here is an example:

        ----
        {"example": "1"}
        ----

        Here is another example:

        [source, yaml]
        ----
        example: 2
        ----

        And a third:

        [,python]
        ----
        print("hello")
        ----


    This would yield the following tuples::

        (6, "json", '{"example": "1"}')
        (12, "yaml", 'example: 2')
        (19, "python", 'print("hello")')

    """

    source_language = ""
    qa_markers: set[str] = set()

    iterator = peek_ahead(text)
    for block_start_line, current_line, next_line in iterator:
        # The source-language attribute sets the syntax for the entire document.
        if current_line.startswith(":source-language:"):
            _, _, source_language = current_line.partition(":source-language:")
            source_language = source_language.strip().lower()
            continue

        # Capture check-code-block markers.
        if current_line.lstrip().startswith("//") and current_line[2:].lstrip().startswith("check-code-block:"):
            qa_markers = {
                i.strip()
                for i in current_line.partition("check-code-block:")[2].split(",")
            }
            continue

        if current_line.startswith("[") and "," in current_line:
            # Explicit or implicit source code block.
            block_syntax = current_line.split(",")[1].strip("] ").lower()
            # Consume blank lines between the header and the content (or dashes).
            while next_line is not None and next_line.rstrip() == "":
                block_start_line, current_line, next_line = next(iterator)
            # Determine if the code block is delimited by blank lines or dashes.
            # If delimited by dashes, the number must be at least four,
            # and the exact number must be tracked to support nesting.
            closing_dashes = ""
            if next_line.rstrip().startswith("----"):
                closing_dashes = next_line.rstrip()
            block_start_line, current_line, next_line = next(iterator)
            if closing_dashes and next_line is not None:
                block_start_line, current_line, next_line = next(iterator)

        elif current_line.rstrip().startswith("----") and source_language:
            # Code listing with a known source language.
            block_syntax = source_language
            closing_dashes = current_line.rstrip()
            block_start_line, current_line, next_line = next(iterator)

        else:
            # No source code block found.
            continue

        # *current_line* now contains the first line of content.
        block_lines = []
        while True:
            if closing_dashes and current_line.rstrip() == closing_dashes:
                break
            if not closing_dashes and current_line.rstrip() == "":
                break
            block_lines.append(current_line)
            if next_line is None:
                break
            _, current_line, next_line = next(iterator)

        yield block_start_line, block_syntax, "\n".join(block_lines), qa_markers

        # Reset.
        qa_markers = set()
