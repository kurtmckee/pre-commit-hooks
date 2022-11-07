from __future__ import annotations
import pathlib
import typing as t

import pytest

import hooks.check_code_block_syntax as ccbs


files = pathlib.Path(__file__).parent / "files"


def load_file_tests() -> t.Generator[pytest.param]:
    for file in files.rglob("*/*.*"):
        text = file.read_text()
        blocks = []
        errors = []
        for line in text.splitlines():
            if line.startswith("Blocks: "):
                blocks = eval(line.partition("Blocks: ")[2])
            if line.startswith("Errors: "):
                errors = eval(line.partition("Errors: ")[2])
            if not line.strip():
                break
        yield pytest.param(file, text, blocks, errors, id=str(file.relative_to(files)))


@pytest.mark.parametrize("path, text, blocks, errors", load_file_tests())
def test_files(path, text, blocks, errors):
    if path.suffix == ".rst":
        assert list(ccbs.restructuredtext.get_code_blocks(text)) == blocks
    elif path.suffix == ".md":
        assert list(ccbs.markdown.get_code_blocks(text)) == blocks
    elif path.suffix == ".adoc":
        assert list(ccbs.asciidoc.get_code_blocks(text)) == blocks

    for block, error in zip(blocks, errors):
        if block[1] == "json":
            assert ccbs.json_.check_syntax(block[2]) == error
        elif block[1] == "python":
            assert ccbs.python_.check_syntax(block[2]) == error
