---
layout: post
title:  Python Packging: Extras versus Dependency Groups
categories: [python, tutorials, poetry, uv]
excerpt: Making pyproject.toml compatible with multiple build systems (Poetry and uv)
---

Poetry is a popular dependency management and packing tool for Python, but it doesn't strictly follow certain Python Enhancement Proposals (PEPs). This makes a `pyproject.toml` file written for `Poetry` incompatible with other build systems, like `uv`. In January 2025, Poetry released a [major update](https://python-poetry.org/blog/announcing-poetry-2.0.0/) to be incompliance with several PEPs. Let's see how a `pyproject.toml` file for `Poetry 2.x` can be written to be compatible with build systems like `uv`.

Our goal here is to:
1. Transition a `pyproject` file from Poetry 1.x to 2.x
2. Have our newly migrated `pyproject` file compatible with other build systems, like `uv`
3. Gain a deeper understanding of the `pyproject.toml` file to correctly package our projects

- [Major differences between Poetry 1.x and 2.x](#major-differences-between-poetry-1x-and-2x)
- [Dependency groups vs Extras](#dependency-groups-vs-extras)
  - [Optional Dependencies (Extras)](#optional-dependencies-extras)
  - [Dependency Groups](#dependency-groups)
  - [Useing both Extras and Groups](#useing-both-extras-and-groups)
- [In a monorepo context](#in-a-monorepo-context)
  - [Example files](#example-files)
- [Cross-system compatibility](#cross-system-compatibility)


# Major differences between Poetry 1.x and 2.x
* Project metadata is moved from the `[tool.poetry]` table to the `[project]` table (PEP 621)
* Python version specification is now defined by the `requires-python` key under `[project]`
* Dependencies are moved from `[tool.poetry.dependencies]` to the `dependencies` key under `[project]` (PEP 508, [see docs](https://python-poetry.org/docs/dependency-specification/))
* Optional dependencies are moved from `[tool.poetry.dependencies]` to `[project.optional-dependencies]` -- There are some nuances here, see the sections on Optional Dependencies.

# Dependency groups vs Extras
This is a point I was unfamiliar with, but they're important concepts core to properly format `pyproject` files. It is worth reading [PEP 735](https://peps.python.org/pep-0735/) to gain a deeper understanding of the Limitations of `requirement.txt` files and `extras`. 

## Optional Dependencies (Extras)
Extras are a standardized Python packaging concept defined in PEP 508, so it is recognized by various packaging tools. Users can install extras via `pip install package[extra_name]`.

Poetry 2.x allows optional dependencies to be specified like this ([docs](https://python-poetry.org/docs/pyproject/#dependencies)):
```toml
[project.optional-dependencies]
mysql = [ "mysqlclient>=1.3,<2.0" ]
pgsql = [ "psycopg2>=2.9,<3.0" ]
databases = [ "mysqlclient>=1.3,<2.0", "psycopg2>=2.9,<3.0" ]
```

Extras are primarily for end-users to select optional features. This implies that the current project is a package (as opposed to non-package projects, such as many datascience projects). Because an extra defines optional additional dependencies, it is not possible to install an extra without installing the current package and its dependencies.

## Dependency Groups
Dependency groups are used by poetry to allow developers to organize dependencies by development context. These groups are not published to the users.
```
[tool.poetry.dependencies]
python = "^3.8"
requests = "^2.25.1"

[tool.poetry.group.dev.dependencies]
black = "^22.3.0"
flake8 = "^4.0.1"

[tool.poetry.group.test.dependencies]
pytest = "^7.0.0"
pytest-cov = "^3.0.0
```

When `poetry lock` is updated, dependency versions are resolved across all groups. So you can specify versions of subdependencies to address CVE concerns:
```
[tool.poetry.group.subdep.dependencies]
# version restrictions due to security concerns
h11 = "^0.16"
requests = "^2.32.0"
```

Because dependency groups are primarily used for developers, you can specify that you only want to install the `test` group without installing the main dependency group. This behavior is the opposite from that of Extras.

Dependency groups _were_ a Poetry-specific concept. In October 2024, Python adopted [PEP 735](https://peps.python.org/pep-0735/) to define how dependency groups are specified. However, Poetry is not yet compatible with PEP 735 (see the [open issue](https://github.com/python-poetry/poetry/issues/9751)). So for now, we need to keep using Poetry's tool-specific dependency groups, defined in the `tool.poetry` section.

Note: `uv` does support dependency groups specified in the PEP 735 format.

## Useing both Extras and Groups
If you want to define additional information that is not required for building but only for locking (for example, an explicit source), you can enrich dependency information in the tool.poetry section.
```
[project]
# ...
dependencies = [
    "requests>=2.13.0",
]

[tool.poetry.dependencies]
requests = { source = "private-source" }
```
When both are specified, project.dependencies are used for metadata when building the project, tool.poetry.dependencies is only used to enrich project.dependencies for locking.

You can enrich optional dependencies for locking in the tool.poetry section analogous to dependencies.

# In a monorepo context
The root monorepo is not intended to be built as a package, so the `pyproject.toml` needs to be adjusted slightly.

1. Relative Paths 
(taken straight from [the docs](https://python-poetry.org/docs/dependency-specification/))

You can add `dependencies` to `dynamic` and define your dependencies completely in the `tool.poetry` section. Using only the `tool.poetry` section might make sense in non-package mode when you will not build an sdist or a wheel.

```
[project]
# ...
dynamic = [ "dependencies" ]

[tool.poetry.dependencies]
requests = { version = ">=2.13.0", source = "private-source" }
```
Another use case for tool.poetry.dependencies are relative path dependencies since `project.dependencies` only support absolute paths.


## Example files
```
[project]
name = "monorepo-wrapper"
description = ""
license = "MIT"
dynamic = ["version"]
readme = "README.md"
authors = [{name = "Your Name", email = "you@example.com"}]
requires-python = '>=3.10,<4.0'
dependencies = []

[tool.poetry]
version = "0.1.0"

[tool.poetry.dependencies]
my_project = {path ="./my_project", develop=true}
plugin = {path ="./plugins/my_plugin", develop=true, extras=['test']}
```
Try running `poetry install` and `uv sync`. They should both work. You should also find your plugin installed along with its extra "test" dependencies.


```
[project]
name = "my_plugin"
description = ""
license = "MIT"
dynamic = ["version"]
readme = "README.md"
authors = [{name = "Your Name", email = "you@example.com"}]
requires-python = '>=3.10,<4.0'
dependencies = [
    'numpy (>=2.0.2) ; python_version >= "3.10"',
]

[tool.poetry]
version = "0.1.0"

[project.optional-dependencies]
test = [
    "pytest (>=8.2.2,<9.0.0)", 
]

[build-system]
requires = ["poetry-core>=2.0.0,<3.0.0"]
build-backend = "poetry.core.masonry.api"
```
Try running `poetry install` and `uv sync`. They should both work. But in this case, running `uv sync` will only install the main dependency group. To install the extras, run
```
# install the test group
uv sync --extra test

# install all optional groups
uv sync --all-extras
```

# Cross-system compatibility
With your `pyproject.toml` properly configured, all of the following should work:
```
$ poetry sync --extras dev

$ poetry sync --all-extras

$ uv sync --extra dev

$ uv sync --all--extras
```



Full docs: https://python-poetry.org/docs/pyproject/

References: https://stackoverflow.com/questions/79523584/use-a-single-pyproject-toml-for-poetry-uv-dev-dependencies