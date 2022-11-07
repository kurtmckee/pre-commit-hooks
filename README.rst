Pre-commit hooks
################

The `pre-commit`_ hooks in this repository help me maintain my own projects.

-------------------------------------------------------------------------------

``verify-consistent-pyproject-toml-python-requirements``
========================================================

Enforces that the ``tool.poetry.dependencies.python`` value matches
across ``pyproject.toml`` files in a given repository.

By default, only ``pyproject.toml`` files in a ``requirements/`` subdirectory are checked.
This can be customized by setting ``args`` in the ``.pre-commit.hooks.yaml`` configuration:

..  code-block:: yaml

    - id: "enforce-consistent-pyproject-toml-python-version-requirements"
      args: ["test-requirements", "docs-requirements"]

`Poetry`_ requires that all dependencies in all dependency groups must be internally consistent,
but I typically don't want my testing dependencies to affect my package dependencies.
(For example, the dependencies for static type analysis and documentation builds
don't need to be internally consistent with the project requirements.)
To support independent dependency resolution, I currently create separate ``pyproject.toml`` files,
have Poetry resolve the dependencies, and export the requirements to ``pip``-installable text files.

To help ensure that the secondary ``pyproject.toml`` files' Python requirements stay maintained,
this hook verifies that the Python requirements (like ``">=3.8"``) match across all files.


..  Links
..  -----
..
..  _pre-commit: https://pre-commit.com/
..  _Poetry: https://python-poetry.org/
