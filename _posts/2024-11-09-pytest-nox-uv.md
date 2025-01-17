---
layout: post
title:  Testing your code in multiple environments with nox and uv
categories: [Python, Tutorials, virtual environments, pytest, uv, nox, poetry]
excerpt: Often in production, you might want to test your code in different python versions or environment variables. You could use the `matrix` command in Github CI, but it's much more tedious to do the same thing locally. Instead of manually setting up each environment and variable, Nox helps you automate this kind of testing. Let's see what it takes to set up Nox and test my Poetry-managed package in three different Python environments.
---
Often in production, you might want to test your code in different python versions or environment variables. You could use the `matrix` command in Github CI, but it's much more tedious to do the same thing locally. Instead of manually setting up each environment and variable, Nox helps you automate this kind of testing. Let's see what it takes to set up Nox and test my Poetry-managed package in three different Python environments.

In this post:
- [Nox in a nutshell](#nox-in-a-nutshell)
- [Testing a Poetry-managed package with Nox](#testing-a-poetry-managed-package-with-nox)
  - [Install the desired python versions](#install-the-desired-python-versions)
  - [Install nox and (optional) nox-poetry](#install-nox-and-optional-nox-poetry)
  - [Set up noxfile.py for uv installation (preferred)](#set-up-noxfilepy-for-uv-installation-preferred)
  - [Set up noxfile.py for Poetry installation (no longer preferred)](#set-up-noxfilepy-for-poetry-installation-no-longer-preferred)
- [Other common Nox uses](#other-common-nox-uses)
- [Wrapping up](#wrapping-up)


# Nox in a nutshell
First, there was Tox. Tox is a CLI tool to automate and standardize testing in python. Its options are stored in a config file, which can be a `.ini` or a `.toml` file. In fact, its configs can also be stored in your `pyproject.toml` file. However, config files can be limiting. Tox grants Python users more freedom by storing test configurations in a Python file instead.

If you're familiar with GNU Make, "sessions" in Nox are similar to "targets" in Make. In fact, you can do everything that Tox or Nox does in a Makefile. But Makefiles are general-purpose and has a high learning curve for new users. So, Python users can quickly get started with Nox. Perhaps this is the reason why Nox is part of the [Hypermodern Cookiecutter](https://github.com/cjolowicz/cookiecutter-hypermodern-python). Side note: the Hypermodern Cookiecutter was last released on 2022.06.23.

When you run Nox, a new virtual environment is created in each "session", and the commands within the session definitions are executed in sequence. This is how Nox can help your tests run in controlled environments.

# Testing a Poetry-managed package with Nox
## Install the desired python versions
If your system does not already have the right python versions available, the tests will obviously fail. Let's use `uv` to install them.

First, set up `uv`. Keep in mind `uv` **must be installed globally**
```sh
pipx install uv
```
or
```sh
pip install uv
```
Install desired python versions with
```sh
uv python install 3.11 3.12 -vvv
```

The `-vvv` flag prints out debugging messages. There's an [issue](https://github.com/astral-sh/uv/issues/8812) with `uv` where it shows the Python installation as successful when it actually failed.

> ! If you run into `invalid peer certificate: UnknownIssuer solution` issues, run `export SSL_CERT_FILE=/etc/ssl/certs/ca-certificates.crt` in console then try again. ([source](https://github.com/astral-sh/uv/issues/1819))

edit 2024-11-09: As I was writing this, an update to Nox was made; you can set the default backend of Nox to use `uv` as you run your test: 
```sh
nox --default-venv-backend uv mytest.py
```
Or add the following to your noxfiles to use `uv` in specific projects:
```py
nox.options.default_venv_backend = "uv|virtualenv"
```
Or specify the session backend with
```py
@nox.session(venv_backend='uv')
```


## Install nox and (optional) nox-poetry
Nox will use the specified backend to install your packages, defaulting to `pip`. Currently, other supported back ends are `uv`, `conda`, `mamba`, and `micromamba`. If you want to use Poetry for installation, you must install the `nox-poetry` package.

Install Nox globally. If using `pipx`:
```sh
pipx install nox
pipx inject nox nox-poetry
```
Otherwise,
```sh
pip install nox
pip install nox-poetry
```

## Set up noxfile.py for uv installation (preferred)
Here an example to run your tests with Python versions 3.10, 3.11, and 3.12. In each session, Nox will 
1. use uv to install your dependencies (without the `dev` group), 
2. Install pytest plugins
3. Run tests with the parameters shown

```py
import nox

python_versions = ["3.10", "3.11", "3.12"]

@nox.session(python=python_versions, venv_backend='uv')
def tests(session):
    """Run tests on specified Python versions."""
    # Install the package and test dependencies
    session.run_always("uv", "pip", "install", ".", external=True)
    
    session.install(
        "pytest-xdist",
        "pytest-randomly",
        "pytest-sugar",
    )
    
    # Run pytest with common options
    session.run(
        "pytest",
        "tests/",
        "-v",                   # verbose output
        "-s",                   # don't capture output
        "--tb=short",           # shorter traceback format
        "--strict-markers",     # treat unregistered markers as errors
        "-n", "auto",           # parallel testing
        *session.posargs        # allows passing additional pytest args from command line
    )
```

Finally, run the tests with nox:

```sh
nox -s tests
```

et voila.

## Set up noxfile.py for Poetry installation (no longer preferred)
Here an example to run your tests with Python versions 3.10, 3.11, and 3.12. In each session, Nox will 
1. use Poetry to install your dependencies (without the `dev` group), 
2. Install pytest plugins
3. Run tests with the parameters shown

```py
from nox_poetry import session

python_versions = ["3.10", "3.11", "3.12"]

@session(python=python_versions, venv_backend='uv')
def tests(session):
    """Run tests on specified Python versions."""
    # Install the package and test dependencies
    session.run_always("poetry", "install", "--without", "dev", external=True)
    
    session.install(
        "pytest-xdist",
        "pytest-randomly",
        "pytest-sugar",
    )
    
    # Run pytest with common options
    session.run(
        "pytest",
        "tests/",
        "-v",                   # verbose output
        "-s",                   # don't capture output
        "--tb=short",           # shorter traceback format
        "--strict-markers",     # treat unregistered markers as errors
        "-n", "auto",           # parallel testing
        *session.posargs        # allows passing additional pytest args from command line
    )
```

Finally, run the tests with nox:

```sh
nox -s tests
```

et voila.

But notice that installing requirements with Poetry is much slower than uv.

# Other common Nox uses
Since Nox is just like Make, you can run the sessions to do much more than testing, [such as](https://nox.thea.codes/en/stable/cookbook.html):
* Creating Dev Environments
* Auto-Release your project
* Use it with Github Actions (just like a makefile)

# Wrapping up
By following this guide, you've gained the tools to efficiently test Python code across multiple environments locally using Nox and uv. Instead of the manual setup for each Python version, you can now automate the process, ensuring consistent testing and compatibility across environments. You've learned how to install multiple Python versions with uv, configure Nox to handle testing with Poetry dependencies, and create flexible, reusable test sessions. This setup not only saves time but also brings you closer to a robust, production-ready development workflow. Happy testing!