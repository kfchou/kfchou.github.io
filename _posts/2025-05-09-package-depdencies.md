---
layout: post
title:  Dependencies in Python Packaging
categories: [python, tutorials, poetry, uv, dependency management]
excerpt: Making our Poetry-based pyproject.toml compatible with uv, and gaining a deeper understanding of pyproject.toml files.
---

Managing dependencies in Python projects can be challenging, especially when working across different tools and build systems. Poetry, a popular dependency management and packaging tool, simplifies many aspects of this process but introduces its own nuances. With the release of Poetry 2.x in January 2025, significant changes were made to align with Python Enhancement Proposals (PEPs), improving compatibility with other tools like uv.

I've been managing projects built with Poetry 1.x. But as use cases evolve to become more complicated, I'm finding it necessary to transition to Poetry 2.x. Additionally, the [advantages of uv]({% post_url 2025-1-16-ode-to-uv %}) are becoming harder to ignore, hence the desire for uv compatibility. This blog explores how to effectively manage dependencies in Python projects beyond the basics. Some key takeaways are:
1. The `[project]` table in `pyproject.toml` is a standard defined by Python Enhancement Proposals. It contains metadada that is parsed by packaging indices such as PyPI. The information included in this table is intended to be readable by all build systems (although Poetry is not compatible with the latest PEPs). 
2. To be usable across different build systems, tool specific options defined in `[tool.poetry]` must be redundantly defined in `[tool.uv]`.
3. Developers must distinguish "Optional Dependencies" from "Dependency Groups" and the context in which they're used.

By the end of this post, you'll have a clear understanding of how to structure your `pyproject.toml` file for maximum compatibility and flexibility, whether you're building a package or managing dependencies in a monorepo.

In this post:
- [A note about pyproject.toml files](#a-note-about-pyprojecttoml-files)
- [Making Poetry compatible with uv](#making-poetry-compatible-with-uv)
  - [Major differences between Poetry 1.x and 2.x](#major-differences-between-poetry-1x-and-2x)
- [Dependency Groups vs Optional Dependencies](#dependency-groups-vs-optional-dependencies)
  - [Optional Dependencies (Extras)](#optional-dependencies-extras)
  - [Dependency Groups](#dependency-groups)
- [Local Dependencies and Editable Installations](#local-dependencies-and-editable-installations)
  - [Poetry](#poetry)
  - [uv](#uv)
- [A Point of Incompatibility: Non-package Projects](#a-point-of-incompatibility-non-package-projects)

# A note about pyproject.toml files
For a lot of this post to make sense, you need to first have a high-level understanding of `pyproject.toml` files:
* It contains your project metadata and replaces `setup.py`.
* Sections are called "tables" and are marked by `[]`.
* The metadata provided under the `[project]` table is parsed by the Python Packaging Index (PyPI).
* Tool-specific tables are marked with `[tool.xyz]`.

ref:
* What are [toml files](https://toml.io/en/)?
* PyOpenSci's [packaging guide](https://www.pyopensci.org/python-package-guide/package-structure-code/intro.html)

# Making Poetry compatible with uv
If you wish to use Poetry alongside uv, the best way to do this is to move as much information as possible out of tool-specific tables (`[tool.poetry]` and `[tool.uv]`) and instead place that information in the common `[project]` table. For this reason, we must migrate Poetry from 1.x to 2.x, which moves essential metadata from the `[tool.poetry]` table to the `[project]` table.

For other settings and configs set under `[tool.poetry]`, we must define an equivalent setting under `[tool.uv]`.

## Major differences between Poetry 1.x and 2.x
The migration process is made simple via tools like the [Poetry Migration plugin](https://github.com/zyf722/poetry-plugin-migrate). The plugin's README details how the migration is done. You probably won't need to know all the details, but it's useful to gain a high-level understanding of the major differences in case anything goes awry:

- **Project metadata** is moved from the `[tool.poetry]` table to the `[project]` table (PEP 621).
- **Python version specification** is now defined by the `requires-python` key under `[project]`.
- **Dependencies** are moved from `[tool.poetry.dependencies]` to the `dependencies` key under `[project]` (PEP 508, [see docs](https://python-poetry.org/docs/dependency-specification/)).
- **Optional dependencies** are moved from `[tool.poetry.extras]` to `[project.optional-dependencies]`. There are some nuances here, which we will explore in the next section.

Transitioning to Poetry 2.x ensures better compatibility with other tools and aligns with Python's packaging standards. Next, let's dive into the differences between dependency groups and optional dependencies.

# Dependency Groups vs Optional Dependencies
It's important to understand the distinctions between dependency groups and optional dependencies (extras), as they are core to properly formatting `pyproject.toml` files. A `pyproject.toml` file can have both dependency groups and optional dependencies to address different use cases.

For a deeper understanding of these concepts, consider reading [PEP 735](https://peps.python.org/pep-0735/), which discusses the limitations of `requirements.txt` files and `extras`.

## Optional Dependencies (Extras)
Extras are a standardized Python packaging concept defined in PEP 508, recognized by various packaging tools. Users can install extras via `pip install package[extra_name]`. The standard way to define optional package dependencies is by using the `[project.optional-dependencies]` table. This is supported by Poetry 2.x, but not 1.x ([docs](https://python-poetry.org/docs/pyproject/#dependencies)):

```toml
[project.optional-dependencies]
mysql = [ "mysqlclient>=1.3,<2.0" ]
pgsql = [ "psycopg2>=2.9,<3.0" ]
databases = [ "mysqlclient>=1.3,<2.0", "psycopg2>=2.9,<3.0" ]
```

Running `pip install package[databases]` will install your main dependencies and your "databases" dependencies.

Extras are primarily for end-users to select optional features. This implies that the current project is a package (as opposed to non-package projects, such as many data science projects). Because an extra defines optional additional dependencies, it is not possible to install an extra without installing the current package and its dependencies.

Compatibility note: Since optional dependencies are defined under the `[project]` table, this is compatible with both Poetry and uv.

## Dependency Groups
Dependency groups are used by Poetry to allow developers to organize dependencies by development context. These groups are not published to the users.

```toml
[tool.poetry.dependencies]
python = "^3.8"
requests = "^2.25.1"

[tool.poetry.group.dev.dependencies]
black = "^22.3.0"
flake8 = "^4.0.1"

[tool.poetry.group.test.dependencies]
pytest = "^7.0.0"
pytest-cov = "^3.0.0"
```

So when a user wants to `pip install your_package`, only the main groups will be installed.

When `poetry lock` is updated, dependency versions are resolved across all groups. So you can specify versions of subdependencies to address CVE concerns:

```toml
[tool.poetry.group.subdep.dependencies]
# version restrictions due to security concerns
h11 = "^0.16"
requests = "^2.32.0"
```

Because dependency groups are primarily used for developers, you can specify that you only want to install the `test` group without installing the main dependency group (`poetry sync --only test`). You can also [specify multiple subgroups](https://python-poetry.org/docs/cli/#sync) to install. This behavior is the opposite of that of Extras.

Compatibility note: Dependency groups _were_ a Poetry-specific concept. In October 2024, Python adopted [PEP 735](https://peps.python.org/pep-0735/) to define how dependency groups are specified. However, Poetry is not yet compatible with PEP 735 (see the [open issue](https://github.com/python-poetry/poetry/issues/9751)). So for now, we need to keep using Poetry's tool-specific dependency groups, defined in the `tool.poetry` section. However, uv does support the standard `[dependency-groups]` table.

# Local Dependencies and Editable Installations
The `project.dependencies` standard does not support developer-oriented information like editable installations and relative paths. Poetry and uv handle these using tool-specific tables.

Note that you can combine the examples below to use both Poetry and uv in the same project.
## Poetry
```toml
[project]
# ...
dependencies = [
    "httpx",
    "my_package[test]",
    "my_plugin",
]

[tool.poetry.dependencies]
httpx = { git = "https://github.com/encode/httpx" }
my_package = { path = "./my_package", develop = true }
my_plugin = { path = "./plugins/my_plugin", develop = true }
```

When specified, `project.dependencies` are used for metadata when building the project, `[tool.poetry.dependencies]` is only used to enrich `project.dependencies` for locking. You can enrich optional dependencies for locking in the `tool.poetry` section analogous to dependencies.

## uv
To enchrich dependencies with uv, place additional information under `[tool.uv.sources]` ([docs](https://docs.astral.sh/uv/concepts/projects/dependencies/#dependency-sources)):
```toml
[project]
# ...
dependencies = [
    "httpx",
    "my_package[test]",
    "my_plugin",
]

[tool.uv.sources]
httpx = { git = "https://github.com/encode/httpx" }
my_package = { path = "./my_package", editable = true }
my_plugin = { path = "./plugins/my_plugin", editable = true }
```

# A Point of Incompatibility: Non-package Projects
[PEP 735](https://peps.python.org/pep-0735/) specifically mentions that some projects aren't meant to be packaged, such as data science projects. Poetry and `uv` handle these projects differently:
```toml
# --------- uv settings -------- 
[tool.uv]
package = false

# -------- poetry settings -------- 
[tool.poetry]
# package-mode = false # This needs to be toggled on if installing via Poetry
```
If you defined your build-system as `poetry-core`, then the above will not work and you must manually toggle the `package-mode` under `poetry settings`.

Hopefully, these discrepancies will be resolved in the near future.