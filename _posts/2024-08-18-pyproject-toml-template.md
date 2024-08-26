---
layout: post
title:  Pyproject.toml Template
categories: [Templates, Python]
---

If you don't already have a `pyproject.toml` file for your existing project, you should. It is required to use with `pip install .` and with `poetry`. Let's take a look at what a `pyproject` file looks like.

According to the [python packaging guide](https://packaging.python.org/en/latest/guides/writing-pyproject-toml/), `pyproject.toml` is a configuration file used by packaging tools, as well as other tools such as linters, type checkers, etc. There are three possible TOML tables in this file.

* The **[build-system]** table is strongly recommended. It allows you to declare which build backend you use and which other dependencies are needed to build your project.

* The **[project]** table is the format that most build backends use to specify your project’s basic metadata, such as the dependencies, your name, etc. It is part of the [PEP 621](https://www.python.org/dev/peps/pep-0621/) specification, which standardizes how project metadata (such as name, version, authors, etc.) should be declared in a pyproject.toml file. It is designed to be tool-agnostic, allowing different build backends (e.g., setuptools, poetry, flit) to interpret the project metadata consistently.

* The **[tool]** table has tool-specific subtables, e.g., [tool.hatch], [tool.black], [tool.mypy]. We only touch upon this table here because its contents are defined by each tool. Consult the particular tool’s documentation to know what it can contain.

In short, **the way the pyproject file is written may depend on the backend build-system** you're using

# pyproject.toml examples
If you're starting a new python project, I highly recommend you create a blank project using the [Hypermodern Cookiecutter](https://github.com/cjolowicz/cookiecutter-hypermodern-python) packaging tool. Walk through the setup process, and it will create a new pyproject.toml file for you.

If you want to add a file to an existing project, see the examples below:

## A minimal pyproject file using `setup-tools` backend:
```toml
[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"

[project]
name = "my_project"
version = "0.1.0"
description = "A minimal Python project"
authors = [
    { name="Your Name", email="your.email@example.com" }
]
dependencies = [
    numpy = "^1.25.2"
    pandas = "^2.0.0"
]
```

## Using `poetry` as backend
You can have `poetry` create a pyproject file for you:
```bash
poetry init --no-interaction
```

Let's take a look at how a toml file is used in Microsoft's [graphrag](https://github.com/microsoft/graphrag) package. Notice that instead of a `[project]` table, it defines all metadata with `[tool.poetry]`. This is considered an older standard, but considering how `poetry` is still the preferred modern package manager, many many projects still write their `pyproject` file this way.

Here's an example:

```toml
# here we specify that the built-system backend is poetry
[build-system]
requires = ["poetry-core>=1.0.0"]
build-backend = "poetry.core.masonry.api"

[tool.poetry]
name = "your_project_name"
version = "X.Y.Z"
description = "project_description"
authors = [
    "First Last <name@domain.com>",
]
maintainers = ["First Last <name@domain.com>",]
license = "MIT"
readme = "README.md"
homepage = "https://github.com/yunojuno/poetry-template"
repository = "https://github.com/yunojuno/poetry-template"
documentation = "https://github.com/yunojuno/poetry-template"
packages = [{ include = "my_package" }]

[tool.poetry.dependencies]
python = ">=3.10,<3.13"
environs = "^11.0.0"
datashaper = "^0.0.49"
# data science
numba = "0.60.0"
numpy = "^1.25.2"
graspologic = "^3.4.1"
networkx = "^3"
fastparquet = "^2024.2.0"
# 1.13.0 was a footgun <--- reason for specific versions
scipy = "1.12.0"

[tool.poetry.group.dev.dependencies]
coverage = "^7.6.0"
ipykernel = "^6.29.4"
jupyter = "^1.0.0"
nbconvert = "^7.16.3"
pytest = "^8.3.2"
pytest-asyncio = "^0.23.4"
pytest-timeout = "^2.3.1"
ruff = "^0.5.2"
semversioner = "^2.0.3"
update-toml = "^0.2.1"
```

# More Template Examples
* If using 'setuptools' as back end, see the [setup-tools specific guide](https://setuptools.pypa.io/en/latest/userguide/pyproject_config.html)
* Poetry [pyproject example](https://github.com/yunojuno/poetry-template/blob/master/pyproject.toml)
* A [template by pypa](https://github.com/pypa/sampleproject/blob/main/pyproject.toml) with in-depth explanations
