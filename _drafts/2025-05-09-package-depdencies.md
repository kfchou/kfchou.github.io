---
layout: post
title:  Dependencies in Python Packging
categories: [python, tutorials, poetry, uv]
excerpt: Optional Dependencies, Dependency Groups, Local Dependencies, and editable dependencies. And, making your Poetry-based pyproject.toml compatible with uv.
---

Poetry is a popular dependency management and packing tool for Python, but it doesn't strictly follow certain Python Enhancement Proposals (PEPs). This makes a `pyproject.toml` file written for `Poetry` incompatible with other build systems, like `uv`. In January 2025, Poetry released a [major update](https://python-poetry.org/blog/announcing-poetry-2.0.0/) to be incompliance with several PEPs. Let's see how a `pyproject.toml` file for `Poetry 2.x` can be written to be compatible with build systems like `uv`.

Our goal here is to:
1. Transition a `pyproject` file from Poetry 1.x to 2.x
2. Have our newly migrated `pyproject` file compatible with other build systems, like `uv`
3. Gain a deeper understanding of "optional dependencies" and "dependency groups" to correctly package our projects
4. Illustrate how to deal with dependencies specified with local paths

In this note:
- [Major differences between Poetry 1.x and 2.x](#major-differences-between-poetry-1x-and-2x)
- [Dependency Groups vs Optional Dependencies](#dependency-groups-vs-optional-dependencies)
  - [Optional Dependencies (Extras)](#optional-dependencies-extras)
  - [Dependency Groups](#dependency-groups)
- [Enriching Dependencies](#enriching-dependencies)
- [Dependencies with Local Paths](#dependencies-with-local-paths)
  - [Illustrating cross-system compatibility -- Example files](#illustrating-cross-system-compatibility----example-files)
- [Caveat: Local Dependencies with uv](#caveat-local-dependencies-with-uv)


# Major differences between Poetry 1.x and 2.x
The migration process is made simple via tools like the [Poetry Migration plugin](https://github.com/zyf722/poetry-plugin-migrate). The plugin's readme details how the migration is done. You probably won't need to know all the details, but it's useful to gain a high level understanding of the major differences in case anything goes awry:
* Project metadata is moved from the `[tool.poetry]` table to the `[project]` table (PEP 621)
* Python version specification is now defined by the `requires-python` key under `[project]`
* Dependencies are moved from `[tool.poetry.dependencies]` to the `dependencies` key under `[project]` (PEP 508, [see docs](https://python-poetry.org/docs/dependency-specification/))
* Optional dependencies are moved from `[tool.poetry.dependencies]` to `[project.optional-dependencies]` -- There are some nuances here, see the sections on Optional Dependencies.

# Dependency Groups vs Optional Dependencies
It's important to understand the distinctions between dependency groups and optional dependencies (extras), since they are core to properly format `pyproject` files. It is worth reading [PEP 735](https://peps.python.org/pep-0735/) to gain a deeper understanding of the Limitations of `requirement.txt` files and `extras`. 

## Optional Dependencies (Extras)
Extras are a standardized Python packaging concept defined in PEP 508, so it is recognized by various packaging tools. Users can install extras via `pip install package[extra_name]`.

Poetry 2.x allows optional dependencies to be specified like this ([docs](https://python-poetry.org/docs/pyproject/#dependencies)):
```py
[project.optional-dependencies]
mysql = [ "mysqlclient>=1.3,<2.0" ]
pgsql = [ "psycopg2>=2.9,<3.0" ]
databases = [ "mysqlclient>=1.3,<2.0", "psycopg2>=2.9,<3.0" ]
```
Running `pip install package[databases]` will install your main dependencies and your "databases" dependencies.

Extras are primarily for end-users to select optional features. This implies that the current project is a package (as opposed to non-package projects, such as many datascience projects). Because an extra defines optional additional dependencies, it is not possible to install an extra without installing the current package and its dependencies.


## Dependency Groups
Dependency groups are used by Poetry to allow developers to organize dependencies by development context. These groups are not published to the users.
```py
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
So when a user wants to `pip install your_package`, only the main groups will be installed.

When `poetry lock` is updated, dependency versions are resolved across all groups. So you can specify versions of subdependencies to address CVE concerns:
```py
[tool.poetry.group.subdep.dependencies]
# version restrictions due to security concerns
h11 = "^0.16"
requests = "^2.32.0"
```

Because dependency groups are primarily used for developers, you can specify that you only want to install the `test` group without installing the main dependency group (`poetry sync --only test`). You can also [specify subgroups](https://python-poetry.org/docs/cli/#sync) to install. This behavior is the opposite from that of Extras.

Dependency groups _were_ a Poetry-specific concept. In October 2024, Python adopted [PEP 735](https://peps.python.org/pep-0735/) to define how dependency groups are specified. However, Poetry is not yet compatible with PEP 735 (see the [open issue](https://github.com/python-poetry/poetry/issues/9751)). So for now, we need to keep using Poetry's tool-specific dependency groups, defined in the `tool.poetry` section.

Note: `uv` does support dependency groups specified in the PEP 735 format.

# Enriching Dependencies
If you want to define additional information that is not required for building but only for locking (for example, an explicit source), you can enrich dependency information in the `[tool.poetry]` table.
```py
[project]
# ...
dependencies = [
    "requests>=2.13.0",
]

[tool.poetry.dependencies]
requests = { source = "private-source" }
```
When both are specified, `project.dependencies` are used for metadata when building the project, `[tool.poetry.dependencies]` is only used to enrich `project.dependencies` for locking.

You can enrich optional dependencies for locking in the `tool.poetry` section analogous to dependencies.

# Dependencies with Local Paths
We might specify local packages as dependencies using local paths (e.g., if you're in a monorepo). The interactions between `pyproject.toml` files becomes tricky, and using Poetry alone as some drawbacks. My biggest complaint is that the [Poetry-Auto-Export](https://github.com/Ddedalus/poetry-auto-export) plugin produces `requirement.txt` files of path-defined dependencies with absolute paths. This behvaior would break during Github CI and other different contexts. This was the main motivation to make my `pyrpoject.toml` files compatible with `uv` 

`project.dependencies` only support absolute paths. In Poetry, this is handled by setting `dependencies` to be `dynamic`, and define those dependencies in the `tool.poetry` table:

```py
[project]
# ...
dynamic = [ "dependencies" ]

[tool.poetry.dependencies]
requests = { version = ">=2.13.0", source = "private-source" }
```

Using only the `tool.poetry` section also makes sense in non-package mode when you will not build an sdist or a wheel.


## Illustrating cross-system compatibility -- Example files
Let's see how local dependencies interact. First, create a top-level pyproject.toml file.
```py
# top level pyproject.toml
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

Then create a minimal "my_plugin" package with this `pyproject.toml` file:
```py
# dependency package's pyproject.toml
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
Once the files are in place, change your working directory to the top level. Try running `poetry install` and `uv sync`. They should both work. You should also find your plugin installed along with its extra "test" dependencies.

Now, navigate to your plugin's directory. Try running `poetry install` and `uv sync`. They should both work. But in this case, running `uv sync` will only install the main dependency group. To install the extras, run
```
# install the test group
uv sync --extra test

# install all optional groups
uv sync --all-extras
```
see another example [here](https://stackoverflow.com/questions/79523584/use-a-single-pyproject-toml-for-poetry-uv-dev-dependencies).

# Bonus/Caveat: Install Local Packages in Editable Mode
Unforutnately, the way packages are specified as editable in Poetry and UV are not yet compatible. You would need to define your editable packages in one way or another (or both, if you want to use both Poetry and UV):

```
# top level pyproject.toml
[project]
...
dependencies = [
    "my_package[test]",
    "my_plugin",
]

# --------- uv settings -------- 
[tool.uv]
package = false

[tool.uv.sources]
my_package = { path = "./my_package", editable = true, extras = ["test"] }
my_plugin = { path = "./plugins/my_plugin", editable = true }

[tool.hatch.metadata]
allow-direct-references = true

# -------- poetry settings -------- 
[tool.poetry]
version = "0.1.0"
# package-mode = false #this need to be toggled on if installing via Poetry

[tool.poetry.dependencies]
my_package = {path = "./my_package", develop=true, extras = ["test"]}
my_plugin = {path = "./plugins/my_plugin", develop=true}
```
Hopefully, these discrepencies will be resolved in the near future.