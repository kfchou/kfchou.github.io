---
layout: post
title:  uv & Python Virtual Environment Tools
categories: [Python, Tutorials, virtual environments, uv]
---

[uv](https://docs.astral.sh/uv/) is a super fast Python package and project manager, written in Rust. It purports to be a drop-in replacement for many of the familiar tools we use, such as Pip, Conda, Poetry, Virtualenv, Pipx, etc... But how realistic is this? What is the developer experience if we ditch our existing tools for uv? Kevin Renskers wrote a nice [comparison](https://www.loopwerk.io/articles/2024/python-poetry-vs-uv/) between Poetry and uv, and came to the conclusion that the number one strength of uv is in how it manages virtual environments. So in this brain dump, I'll focus on virtual environment management aspect of uv, and compare it to other tools like poetry, conda, and virtualenv.

- [A quick snapshot of uv's strengths](#a-quick-snapshot-of-uvs-strengths)
- [The state of virtual environment tools](#the-state-of-virtual-environment-tools)
- [Detailed Comparison](#detailed-comparison)
    - [uv](#uv)
    - [Virtualenv](#virtualenv)
    - [Venv](#venv)
    - [pyenv-virtualenv](#pyenv-virtualenv)
    - [Conda](#conda)
    - [Poetry](#poetry)
- [Conclusion](#conclusion)


# A quick snapshot of uv's strengths
As a data scientist, I used to use Conda to manage everything, from packages to dependencies to virtual environments. But Conda is burdensome to set up and resource intensive. It is also extremely slow, especially when it encounters dependency conflicts. So I switched to Poetry and have had a great experience so far, except for how it deals with python versions and virtual environments. uv promises to solve all of these issues.

Kevin Renskers did a [concise comparison](https://www.loopwerk.io/articles/2024/python-poetry-vs-uv/) between poetry and uv:
* 👍 uv is by far the easiest tool to install, with the least amount of pre-requisites. Unlike Poetry, it does not depend on Python.
    ```bash
    # standalone installer
    curl -LsSf https://astral.sh/uv/install.sh | sh

    # brew
    brew install uv
    ```
* ❌ uv cannot handle dependency groups. Unlike Poetry, which users can specify groups for prod and dev, uv does not support this feature.
* ❌ uv does not have a function to inspect outdated dependencies. Where as you can do so with 
    ```bash
    poetry show --outdated --top-level --with dev --with prod
    ```
    But both tools allow you do update all dependencies easily.
* 👍 uv replaces pipx. Pipx is used to "install and run Python applications in isolated environments". The apps are also added to your PATH variable. Both tools have similar syntaxes for this task, but uv is much faster.
* 👍 uv replaces pyenv. uv does a phenomenal job at virtual environment management and outperforms all other options.

This last point intrigues me, so let's dive in and see why.

# The state of virtual environment tools
First, let me differentiate between a virtual environment tool (something used to create virtual environments) versus a virtual environment manager (a tool to manage multiple virtual environments and control python versions). A virtual environment manager includes tools to create virtual environments.

[virtualenv](https://virtualenv.pypa.io/en/latest/) is a tool to create isolated Python environments. Since Python 3.3, a subset of it has been integrated into the native python [venv module](https://docs.python.org/3/library/venv.html). But you cannot create environments with different python versions with `venv`. i.e., if your base python version is 3.7, you cannot create an environment with python 3.8. Therefore, `venv` is often used in conjunction with [`pyenv`](https://github.com/pyenv/pyenv) - a python version management tool. But having two separate tools is a pain, so [pyenv-virtualenv](https://github.com/pyenv/pyenv-virtualenv) was created to combine virtual environment creation with environment-sepcific python version control.

Over time, tools that combined package, dependency, and virtual environment management became available. Each has their strengths and weaknesses. [Conda](https://docs.conda.io/en/latest/) is great for environment management, since it can handle non-python packages as well, but it is extremely slow and can be complex to set up. [Poetry](https://python-poetry.org/docs/) is much better at dependency management and packaging, but is not designed to be an environment manager and is not suited to wrangle multiple environments and python versions per project. 

[uv](https://docs.astral.sh/uv/) promises do all of these tasks efficiently, but so far, it seems best suited to handle virtual environments purely due to **its speed and its lack of python dependency**. Since it does not depend on python, uv can be used to handle python version management.



| Feature | virtualenv | venv | pyenv | pyenv-virtualenv | conda | poetry | uv* |
|---------|------------|------|-------|-----------------|--------|---------|-------|
| Python Version Management | No | No | Yes | Yes | Yes | Limited | Yes |
| Virtual Environments | Yes | Yes | No | Yes | Yes | Yes | Yes |
| Built-in Package Manager | No (uses pip) | No (uses pip) | No | No (uses pip) | Yes | Yes | Yes |
| Multiple Python Versions | Limited | No | Yes | Yes | Yes | Limited | Yes |
| Non-Python Dependencies | No | No | No | No | Yes | Limited | No |
| System Integration | Good | Good | Excellent | Excellent | Can be complex | Good | Good |
| Resource Usage | Light | Lightest | Light | Medium | Heavy | Medium | Very Light |
| Learning Curve | Medium | Easy | Medium | Medium-High | High | Medium | Easy |
| Dependency Resolution | No | No | No | No | Yes | Yes | Yes |
| Lock File Support | No | No | No | No | Yes | Yes | Yes |
| Build System | No | No | No | No | No | Yes | No |
| Performance | Medium | Medium | N/A | Medium | Slow | Medium | Very Fast |



*This table was generated with a bot so it might not be 100% accurate. uv was less than a year old at the time of writing, so its information may be incomplete


# Detailed Comparison
Let's take a look at what it takes to set up each tool and create virtual environments with specific python versions.

### uv
```bash
# Installation
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Like poetry, uv implicitly creates a virtual environment whenever you use it within a project. However, if you need to explicitly create virtual environments, use a syntax akin to virtualenv:
```bash
# explicitly set up an environment
uv venv <path/myenv> --python 3.11

source <path/myenv>/bin/activate
```
Here, `<path/myenv>` is `.venv` by default. If uv cannot find the specified python version in your system, **uv will download that Python version for you**.

### Virtualenv
You can specify the python interpreter you want to use with the `-p` flag.
```bash
# set up
pip install virtualenv

# Specify Python version
virtualenv myenv --python=python3.9

# Activate/deactivate
source myenv/bin/activate
deactivate
```
If you don't have python3.9 installed, the above commands will error. You'll have to install that python version yourself, and set up your shell alias to ensure that python3.9 points to the correct python interpreter.

### Venv
With venv, you cannot specify the python version for your virtual environment. The default python version will be used.
```bash
# set up - this is necessary if you're using a stripped-down version of python
apt-get python3-venv

# Cannot specify python version
python -m venv <path/myenv>

# Activate/deactivate
source <path/myenv>/bin/activate
deactivate
```

### pyenv-virtualenv
Honestly, setting up pyenv-virtualenv seems burdensome. First, set up [pyenv](https://github.com/pyenv/pyenv). Then set up [pyenv-virtualenv](https://github.com/pyenv/pyenv-virtualenv). The steps are long enough to the point where I will not include it here. But once it's set up, you can use the following to create virtual environments:
```bash
# pyenv-virtualenv
pyenv virtualenv 3.9.0 <myenv-3.9>
pyenv activate <myenv-3.9>
deactivate
```

### Conda
Conda was my preferred virtual environment manager. However, it is only free to organizations with [less than 200 employees](https://docs.anaconda.com/miniconda/). It's also burdensome to set up. If you work on a linux cluster, you'll definitely need to set up a `.condarc` file and specify `proxy servers`, `pkgs_dirs`, `wheel_dirs`, and `env_dirs`.

Anyways, to create a virtual environment:
```bash
conda create -n <env_name> python=<version> --y 
conda activate <env_name> 
conda deactivate
```
Conda will download and install missing python versions, along with any dependencies, inside this new environment. Once inside your environment, you can install packages with `pip`. However, `pip install` may fail if the python version in conda environment differs from the version in the base environment.

Conda also let you manage multiple environments, and this is a big reason why I like it as an environment manager:
```bash
# List all environments
conda env list
# or
conda info --envs

# List packages in current environment
conda list

# List packages in specific environment
conda list -n myenv
```

### Poetry
Poetry automatically creates virtual environments for your project, but it is difficult to create more than one environment, which is needed for testing across different versions of code and dependency versions.
```bash
# Explicitly spawn a virtual environment
poetry shell
```
Inspect your current environment with
```bash
poetry env info
```
And see other environments managed by poetry with
```bash
poetry env list
```
You can use different python installations:
```bash
poetry env use /full/path/to/python

# You can provide an alias if the interpreter is in your PATH
poetry env use python3.7
```
Poetry does not manage different python versions for you.

# Conclusion
Every dev should develop in a virtual environment. I still prefer Poetry because it implicitly sets up a virtual environment for my project, and it handles dependency groups and dependency conflicts efficiently. However, when I run into bugs and need to test across dependency and python versions, I need another tool to help me manage these different environments. 

Conda is easy to use, but burdensome to set up (e.g., in a docker container). It is also slow and resource-intensive. 

Traditional virtual environment tools (virtualenv and venv) either cannot manage python versions, or is budensome to set up as well (pyenv-virtualenv). 

All in all, uv seems to overcome these shortcomings by being **easy to set up** and can **download and manage different python versions** efficiently. Additionally, uv-managed python versions need no additional configuration set up from the user side. So it seems like uv will be making its way into my toolchain.