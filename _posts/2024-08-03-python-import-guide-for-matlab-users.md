---
layout: post
title:  Intro to Python Imports and Modules for Matlab users
categories: [Python, Matlab, Tutorials]
---

When you write a function in MATLAB, each function typically is a single `.m` file. So let's say you've written `my_function()` and saved that function as `my_function.m`. 
To gain access to this function, you would use the `addpath` function to add that script to your MATLAB's search path. After calling `addpath(/path/to/myfolder/)`, which contains `myfunction.m`, then you can call `my_function()`. How do these function imports work in Python?

# Key Concepts
* Functions in Python are organized in modules (`.py` files)
* Modules are organized in packages (directories with `__init__.py` files)
* `__init__.py` files can be empty. See [init files](#init-files), below.
* Each package can contain multiple modules
* A package can only be imported if it's within your python interpreter's search path (see [path management](#path-management))

For example, you might set up a project with `package1` and two modules like this:
```
Project
| - package1
|   | - __init__.py
|   | - module1.py
|   | - module2.py
...
```
# Accessing content in your modules
You can import any named variables (functions, classes, variables, etc) from the module into your script or workspace, provided you've set up your paths correctly (see [path management](#path-management)).

Lets say you have the following module:
```py
# module1.py
def my_function():
    print("Hello from module1")
```
Then in your script, you can import its contents with the syntax
```py
from package import module
```
or
```py
from package.module import variable
```

For example:
```py
# main.py
from package1 import module1 # imports the entire module

my_module.my_function()  # Outputs: Hello from module1
```
You can import a specific variable to avoid any potential namespace conflicts:
```py
# main.py
from package1.module1 import my_function

my_function()  # Outputs: Hello from my_module
```

# Path management

Add packages to your python interpreter search path by one of the following methods:
* Using `sys.path`
  ```py
  import sys
  sys.path.append('/path/to/my/module')
  ```
  Check what is in your search path with
  ```
  print(sys.path)
  ```
* Or by setting the `PYTHONPATH` environment variable. In linux, you can set the `PYTHONPATH` for your current terminal session with:
  ```bash
  export PYTHONPATH=/path/to/your/package
  ```
  If you want to set this up permanently, add the command above to your shell profile (typically in `~/.bashrc`), then load your session profile with
  ```
  source ~/.bashrc  # or the appropriate profile file
  ```
* You may also install your current project with
  ```
  pip install . -e
  ```
  The `.` installs your current project, so make sure your working directory is set to your active project. The `-e` flag enables the changes you make to be reflected immediately in the installed project.

# Init Files
`__init__.py` files are used to mark a directory as a Python package, allowing you to import modules from that directory. When a directory contains an `__init__.py` file, Python treats it as a package, and you can import the modules or sub-packages within it.

Here are a few important things to know about `__init__.py`:
1. `__init__.py` files can be empty, but you'll have to be much more specific about accessing functions inside modules.

    If your init file is empty, then in order to access `func1` in `module1`, you'll have to do
    ```py
    from package1 import module1, module2
    module1.func1()
    module2.func1()
    ```
    Specifically calling `module.function()` can help prevent namespace conflicts.

2. When a package is imported, the code inside the `__init__.py` file is executed. This is useful for setting up package-level variables or importing specific modules.

    Lets say this init file lives within a package called `package1`.
    ```py
    # __init__.py
    from .module1 import some_function as func1
    from .module2 import another_function
    ```
    You would have access to `some_function` by calling
    ```py
    import package1
    package1.func1()
    package1.another_function()
    ```
    This lets you control which functions or variables that users can easily access.