---
layout: post
title:  tbd
categories: [python, tutorials]
excerpt: tbd
---

Q. I have two repositories, each with a "src" package layout. I specify both repositories as dependencies. In my import module, when I inspect the submodules of "src", I see the correct packages listed. Under what circumstances the modules with the same name (in this case, "src") combine and when would the modules overwrite one another?

A. This is an interesting question about Python package namespaces and import behavior. When you have two repositories with the same package name ("src"), there are specific rules that determine whether they'll combine (as namespace packages) or overwrite each other.

## When packages combine (namespace packages)
Packages combine as "namespace packages" under these conditions:

1. **Python 3.3+ implicit namespace packages**: If neither repository has an `__init__.py` file in their "src" directory, Python will treat them as namespace packages and combine their submodules.
2. **Using pkg_resources namespace_packages**: In older Python versions, if both packages declare "src" as a namespace package in their setup.py using:
```
pythonsetup(
    # ...
    namespace_packages=['src'],
    # ...
)
```
In these cases, when you inspect src.__path__, you'll see paths pointing to both repositories, and all submodules from both repositories will be available.

## When packages overwrite each other
Packages will overwrite each other when:

1. **Regular packages with `__init__.py`**: If either or both repositories have an `__init__.py` file in their "src" directory, they're treated as regular packages, not namespace packages.
2. **Import order**: The repository that's imported first (based on sys.path ordering) will take precedence.
3. **Installation order**: With pip, the package installed last typically overwrites earlier ones with the same name.

This overwriting behavior explains why you might only see one set of submodules or experience unpredictable behavior when importing.
How to check which case you have