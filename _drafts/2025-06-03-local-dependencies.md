---
layout: post
title:  Dependencies in Python Packaging
categories: [python, tutorials, poetry, uv, dependency management]
excerpt: Making our Poetry-based pyproject.toml compatible with uv, and gaining a deeper understanding of pyproject.toml files.
---

Your package `app` has a local dependencies. It needs to stay local, perhaps because you're working in a monorepo context, or your company has no private packaging index. How do you handle packing your app?



Your python package "`app`" has a dependency called "`lib_B`", which in turn has a dependency called "`lib_A`". Both `lib_A` and `lib_B` are private local packages.

(Generate a directory tree example)

`lib_B`'s `pyproject.toml` file contains:
```
# if the build-backend is setuptools
[requires]
lib_A @ ../lib_B

# or with Poetry
[tool.poetry.dependencies]
lib_A = { path = "../lib_B" }
```

# Hmm
Each packaging system will parse metadata differently.

# Poetry 1.8
Build you package, then install it
```
poetry build

pip install pist/lib_b-<version>-<other_meta>.whl
```

Inspect the package you installed:
```py
from importlib import metadata
dist = metadata.distribution("lib_B")
dist.requires
```
you'll get something like
```
['lib_b @ file:///home/user/your_project/libs/lib_B']
```

# Poetry 2.x
Inspecting the requirements, you'll see that Poetry 2.x has removed the local path specification
```
['lib_b']
```



“You should not be able to build the package [containing relative path dependencies], since it is not allowed to have dependencies specified as relative paths in package metadata. PEP 508 only allows version specifiers and URL (which only allows absolute paths even if you use file://). ” https://github.com/pypa/pip/issues/9127

sources:
https://github.com/python-poetry/poetry/issues/5273
Discussions:
* https://github.com/python-poetry/poetry/issues/4868
  * "As there is no standard mechanism in wheels to handle relative path dependencies"
  * "Relative paths are problematic. When wheels are being built under PEP-517, the source is expected to be moved into an isolated environment at build time. This means your relative paths will need to hold even when your project source is moved to an ephemeral build directory. ...The general question of "what should this be relative to?" is still an open question within the packaging group. See [here](https://discuss.python.org/t/what-is-the-correct-interpretation-of-path-based-pep-508-uri-reference/2815) for more on this"

