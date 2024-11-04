---
layout: post
title:  Testing your code in multiple environments with Nox, uv, and Poetry
categories: [Python, Tutorials, virtual environments, pytest, uv, nox, peotry]
---

Install uv and nox globally. If using `pipx`:
```
pipx install uv
pipx install nox
pipx inject nox nox-poetry
```
Otherwise,
```
pip install uv
pip install nox
pip nox-poetry
```

Install desired python versions with uv
```
uv python install 3.11 3.12
```


Add the uv python installations to your path so they can be discovered by `nox`
```sh
#!/usr/bin/env bash

p=$PATH
for k in "$(uv python dir)"/*/bin; do
    p="${k}:${p}"
done

PATH=$p "$@"
```


Finally, run the tests with nox
```
sh shim-uv.sh nox -s tests
```