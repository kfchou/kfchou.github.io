---
layout: post
title:  Testing your code in multiple environments with nox and uv
categories: [Python, Tutorials, virtual environments, pytest, uv, nox, poetry]
excerpt: Often in production, you might want to test your code in different python versions or environment variables. You could use the `matrix` command in Github CI, but it's much more tedious to do the same thing locally. Instead of manually setting up each environment and variable, Nox helps you automate this kind of testing. Let's see what it takes to set up Nox and test my Poetry-managed package in three different Python environments.
---
Often in production, you might want to test your code in different python versions or environment variables. You could use the `matrix` command in Github CI, but it's much more tedious to do the same thing locally. Instead of manually setting up each environment and variable, Nox helps you automate this kind of testing. Let's see what it takes to set up Nox and test my Poetry-managed package in three different Python environments.

In this post:
- [Nox in a nutshell](#nox-in-a-nutshell)
- [Set up `uv` to manage python versions and package installations](#set-up-uv-to-manage-python-versions-and-package-installations)
  - [(optional) configure additional settings](#optional-configure-additional-settings)
  - [(optional) Install desired python versions](#optional-install-desired-python-versions)
- [Install nox and (optional) nox-poetry](#install-nox-and-optional-nox-poetry)
- [Set up Noxfile.py](#set-up-noxfilepy)
  - [Set uv as the backend](#set-uv-as-the-backend)
  - [Use uv to handle package installations (preferred)](#use-uv-to-handle-package-installations-preferred)
  - [Poetry installation (no longer preferred)](#poetry-installation-no-longer-preferred)
- [Using Nox to benchmark pip, poetry, and uv](#using-nox-to-benchmark-pip-poetry-and-uv)
- [Other common Nox uses](#other-common-nox-uses)
- [Wrapping up](#wrapping-up)


# Nox in a nutshell
First, there was Tox. Tox is a CLI tool to automate and standardize testing in python. Its options are stored in a config file, which can be a `.ini` or a `.toml` file. In fact, its configs can also be stored in your `pyproject.toml` file. However, config files can be limiting. Tox grants Python users more freedom by storing test configurations in a Python file instead.

If you're familiar with GNU Make, "sessions" in Nox are similar to "targets" in Make. In fact, you can do everything that Tox or Nox does in a Makefile. But Makefiles are general-purpose and has a high learning curve for new users. So, Python users can quickly get started with Nox. Perhaps this is the reason why Nox is part of the [Hypermodern Cookiecutter](https://github.com/cjolowicz/cookiecutter-hypermodern-python). Side note: the Hypermodern Cookiecutter was last updated on 2022.06.23.

When you run Nox, a new virtual environment is created in each "session", and the commands within the session definitions are executed in sequence. This is how Nox can help your tests run in controlled environments.

# Set up `uv` to manage python versions and package installations
If your system does not already have the right python versions available, the tests will obviously fail. Let's use `uv` to install them.

First, set up `uv`. Keep in mind `uv` **must be installed globally**
```sh
pipx install uv
```
or
```sh
pip install uv
```

## (optional) configure additional settings
If working on linux servers with limited home directory space, specify your python installation directory with the `UV_PYTHON_INSTALL_DIR` environment variable. Add to your `bashrc`:
```bash
export UV_PYTHON_INSTALL_DIR=my_python_install_dir
```
See additional settings for `uv` in the [docs](https://docs.astral.sh/uv/configuration/environment/#uv_python_install_dir).

By default, `uv` will also utilize your `~/.cache` directory. So I recommend creating a symlink to a directory that's not space-restricted.
```bash
ln -s my_unrestricted_dir/.cache ~/.cache
```

## (optional) Install desired python versions
This step is optional because `uv` will automatically install missing python versions for you.
```sh
uv python install 3.11 3.12 -vvv
```

The `-vvv` flag prints out debugging messages. There's an [issue](https://github.com/astral-sh/uv/issues/8812) with `uv` where it shows the Python installation as successful when it actually failed. 

> ! If you run into `invalid peer certificate: UnknownIssuer solution` issues, run `export SSL_CERT_FILE=/etc/ssl/certs/ca-certificates.crt` in console then try again. ([source](https://github.com/astral-sh/uv/issues/1819))


# Install nox and (optional) nox-poetry
Nox will use the specified backend to install your packages, defaulting to `pip`. Currently, other supported back ends are `uv`, `conda`, `mamba`, and `micromamba`. If you want to use Poetry for installation, you must install the `nox-poetry` package.

Install Nox globally. If using `pipx`:
```sh
pipx install nox
pipx inject nox nox-poetry # optional
```
Otherwise,
```sh
pip install nox
pip install nox-poetry # optional
```
# Set up Noxfile.py
## Set uv as the backend
edit 2024-11-09: You can now set the default backend of Nox to use `uv`. There are seveeral ways to do this:
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

## Use uv to handle package installations (preferred)
Here is an example to run your tests with Python versions 3.10, 3.11, and 3.12. In each session, Nox will 
1. use uv to install your dependencies (without the `dev` group), 
2. Install pytest plugins
3. Run tests with the parameters shown

```py
import nox

# uv will handle any missing python versions
python_versions = ["3.10", "3.11", "3.12"]

@nox.session(python=python_versions, venv_backend='uv')
def tests(session):
    """Run tests on specified Python versions."""
    # Install the package and test dependencies with uv
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

## Poetry installation (no longer preferred)
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

# Using Nox to benchmark pip, poetry, and uv
uv is build to be much, much faster than pip and poetry. Let's write a noxfile to test whether this is the case.

Here, I assume `pip`, `poetry`, and `uv` are all set up in your system, and you have a `pyproject.toml` file configured for poetry, and a corresponding `requirements.txt` file exists.

```py
import nox
import time

@nox.session(python="3.10",venv_backend='uv')
@nox.parametrize(
    "installer",
    [
        ("pip"),
        ("poetry"),
        ("uv"),
    ]
)
def compare_installers(session, installer):
    if installer == "pip":
        session.run("python", "-m", "ensurepip", "--upgrade")

        start = time.time()
        session.run("python", "-m", "pip", "install", "-r", "requirements.txt", ".")
        elapsed = time.time() - start

        session.log("pip install time: %s", elapsed)
    elif installer == "poetry":
        start = time.time()
        session.run("poetry", "install", "--without", "dev,test,lambda", external=True)
        elapsed = time.time() - start
        
        session.log("poetry install time: %s", elapsed)
    elif installer == "uv":
        start = time.time()
        session.run("uv", "pip", "install", "-r", "requirements.txt", ".")
        elapsed = time.time() - start
        
        session.log("uv install time: %s", elapsed)
```

for my particular dependencies, we can see that `uv` is faster than `poetry`, which is faster than `pip`:
```
nox > pip install time: 38.855388164520264
nox > poetry install time: 8.043816328048706
nox > uv install time: 0.2378978729248047
```
the results are similar to what is shown in the `uv` github repository.

# Other common Nox uses
Since Nox is just like Make, you can run the sessions to do much more than testing, [such as](https://nox.thea.codes/en/stable/cookbook.html):
* Creating Dev Environments
* Auto-Release your project
* Use it with Github Actions (just like a makefile)

# Wrapping up
By following this guide, you've gained the tools to efficiently test Python code across multiple environments locally using Nox and uv. Instead of the manual setup for each Python version, you can now automate the process, ensuring consistent testing and compatibility across environments. You've learned how to install multiple Python versions with uv, configure Nox to handle testing with Poetry dependencies, and create flexible, reusable test sessions. This setup not only saves time but also brings you closer to a robust, production-ready development workflow. Happy testing!