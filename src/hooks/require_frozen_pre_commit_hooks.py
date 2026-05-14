# This file is a part of Kurt McKee's pre-commit-hooks project.
# https://github.com/kurtmckee/pre-commit-hooks
# Copyright 2024-2026 Kurt McKee <contactme@kurtmckee.org>
# SPDX-License-Identifier: MIT

from __future__ import annotations

import pathlib
import sys
import textwrap
import typing as t

RC_SUCCESS: t.Final[t.Literal[0]] = 0
RC_FAILURE: t.Final[t.Literal[1]] = 1


def main() -> t.Literal[0, 1]:
    """Require all pre-commit hooks to be frozen."""

    config = pathlib.Path(".pre-commit-config.yaml")

    try:
        contents = config.read_text(encoding="utf-8")
    except (FileNotFoundError, UnicodeDecodeError):
        # Ignore serious problems.
        return RC_FAILURE

    for line in contents.splitlines():
        if not line.strip().startswith("rev:"):
            continue

        _, _, right = line.partition("#")
        if right.strip().startswith("frozen:"):
            continue

        msg = """
        At least one pre-commit hook is not frozen.

        To fix this, run one of the following commands:

        *   prek auto-update --freeze
        *   pre-commit autoupdate --freeze
        """

        print(textwrap.dedent(msg).strip())
        return RC_FAILURE

    return RC_SUCCESS


if __name__ == "__main__":
    sys.exit(main())
