---
layout: post
title:  Dependencies in Python Packaging
categories: [python, tutorials, poetry, uv]
excerpt: Optional Dependencies, Dependency Groups, Local Dependencies, and editable dependencies. And, making your Poetry-based pyproject.toml compatible with uv.
---

Managing dependencies in Python projects can be challenging, especially when working across different tools and build systems. Poetry, a popular dependency management and packaging tool, simplifies many aspects of this process but introduces its own nuances. With the release of Poetry 2.x in January 2025, significant changes were made to align with Python Enhancement Proposals (PEPs), improving compatibility with other tools like uv.

I've been managing projects built with Poetry 1.x. But as use cases evolve to become more complicated, I'm finding it necessary to transition to Poetry 2.x. Additionally, the [advantages of uv](./2025-1-16-ode-to-uv.md) is becoming harder to ignore, hence the desire for uv compatibility. This blog explores how to effectively manage dependencies in Python projects beyond the basics:
1. Transitioning a `pyproject.toml` file from Poetry 1.x to 2.x
2. Maximizing compatibility with other build systems, such as uv (100% compatibility is not possible as of May 2025). Alternatively, just [migrate fully to uv](https://github.com/mkniewallner/migrate-to-uv)
3. Understanding and leveraging "optional dependencies" and "dependency groups"
4. Handling local dependencies and editable installations in a cross-system environment
5. Installing local dependencies in editable mode in both poetry and uv packaging systems

By the end of this post, you'll have a clear understanding of how to structure your `pyproject.toml` file for maximum compatibility and flexibility, whether you're building a package or managing dependencies in a monorepo.

In this post:
- [Making Poetry compatible with uv](#making-poetry-compatible-with-uv)
  - [Major differences between Poetry 1.x and 2.x](#major-differences-between-poetry-1x-and-2x)
- [Dependency Groups vs Optional Dependencies](#dependency-groups-vs-optional-dependencies)
  - [Optional Dependencies (Extras)](#optional-dependencies-extras)
  - [Dependency Groups](#dependency-groups)
- [Local Dependencies and Editable Installations](#local-dependencies-and-editable-installations)
  - [Poetry](#poetry)
  - [uv](#uv)
- [A point of Incompatibility: Non-package projects](#a-point-of-incompatibility-non-package-projects)

# Making Poetry compatible with uv
If you wish to use Poetry alongside uv, the best way to do this is to move as much information as possible out of tool-specific tables (`[tool.poetry]` and `[tool.uv]`), and instead, place those information in "standard" `[project]` tables accepted by different build tools. For this reason, we must migrate Poetry from 1.x to 2.x, which moves essentiam metadata from the `[tool.poetry]` table to the `[project]` table.

For other settings and configs set under `[tool.poetry]`, we must define an equivalent setting under `[tool.uv]`

## Major differences between Poetry 1.x and 2.x
The migration process is made simple via tools like the [Poetry Migration plugin](https://github.com/zyf722/poetry-plugin-migrate). The plugin's readme details how the migration is done. You probably won't need to know all the details, but it's useful to gain a high-level understanding of the major differences in case anything goes awry:

- **Project metadata** is moved from the `[tool.poetry]` table to the `[project]` table (PEP 621).
- **Python version specification** is now defined by the `requires-python` key under `[project]`.
- **Dependencies** are moved from `[tool.poetry.dependencies]` to the `dependencies` key under `[project]` (PEP 508, [see docs](https://python-poetry.org/docs/dependency-specification/)).
- **Optional dependencies** are moved from `[tool.poetry.dependencies]` to `[project.optional-dependencies]`. There are some nuances here, which we will explore in the next section.

Transitioning to Poetry 2.x ensures better compatibility with other tools and aligns with Python's packaging standards. Next, let's dive into the differences between dependency groups and optional dependencies.

# Dependency Groups vs Optional Dependencies
It's important to understand the distinctions between dependency groups and optional dependencies (extras), as they are core to properly formatting `pyproject.toml` files. A pyproject.toml file can have both depedency groups and optional dependencies to address different use cases.

For a deeper understanding of these concepts, consider reading [PEP 735](https://peps.python.org/pep-0735/), which discusses the limitations of `requirements.txt` files and `extras`.

## Optional Dependencies (Extras)
Extras are a standardized Python packaging concept defined in PEP 508, recognized by various packaging tools. Users can install extras via `pip install package[extra_name]`.

Poetry 2.x allows optional dependencies to be specified like this ([docs](https://python-poetry.org/docs/pyproject/#dependencies)):

```toml
[project.optional-dependencies]
mysql = [ "mysqlclient>=1.3,<2.0" ]
pgsql = [ "psycopg2>=2.9,<3.0" ]
databases = [ "mysqlclient>=1.3,<2.0", "psycopg2>=2.9,<3.0" ]
```

Running `pip install package[databases]` will install your main dependencies and your "databases" dependencies.

Extras are primarily for end-users to select optional features. This implies that the current project is a package (as opposed to non-package projects, such as many data science projects). Because an extra defines optional additional dependencies, it is not possible to install an extra without installing the current package and its dependencies.

Compatibility note: Since optional dependencies are defiend under the `[project]` table, this is compatible with both Poetry and uv.

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

Because dependency groups are primarily used for developers, you can specify that you only want to install the `test` group without installing the main dependency group (`poetry sync --only test`). You can also [specify subgroups](https://python-poetry.org/docs/cli/#sync) to install. This behavior is the opposite from that of Extras.

Compatibility note: Dependency groups _were_ a Poetry-specific concept. In October 2024, Python adopted [PEP 735](https://peps.python.org/pep-0735/) to define how dependency groups are specified. However, Poetry is not yet compatible with PEP 735 (see the [open issue](https://github.com/python-poetry/poetry/issues/9751)). So for now, we need to keep using Poetry's tool-specific dependency groups, defined in the `tool.poetry` section. However, uv does support the standard `[dependency-groups]` table.

# Local Dependencies and Editable Installations
The `project.dependencies` standard does not support developer-oriented information like like editable installations and relative paths. Poetry and uv handles these using tool specific tables.

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
my_package = { path = "./my_package", develop = true}
my_plugin = { path = "./plugins/my_plugin", develop = true }
```

When specified, `project.dependencies` are used for metadata when building the project, `[tool.poetry.dependencies]` is only used to enrich `project.dependencies` for locking. You can enrich optional dependencies for locking in the `tool.poetry` section analogous to dependencies.

## uv
uv has its own table for enriching dependencies ([docs](https://docs.astral.sh/uv/concepts/projects/dependencies/#dependency-sources)):
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
my_package = { path = "./my_package", editable = true}
my_plugin = { path = "./plugins/my_plugin", editable = true }
```

# A point of Incompatibility: Non-package projects
[PEP 735](https://peps.python.org/pep-0735/) specifically mentions that some projects aren't meant to be packaged, such as data science projects. Poetry and `uv` handles these projects differently:
```toml
# --------- uv settings -------- 
[tool.uv]
package = false

# -------- poetry settings -------- 
[tool.poetry]
# package-mode = false #this need to be toggled on if installing via Poetry
```
If you defined your build-system as `poetry-core`, then the above will not work and you must manually toggle the `package-mode` under `poetry settings`.

Hopefully, these discrepancies will be resolved in the near future.