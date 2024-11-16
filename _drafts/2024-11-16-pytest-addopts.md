---
layout: post
title:  TBD
categories: [Python, Tutorials, virtual environments, pytest]
excerpt: 
---

In the past couple of posts, I've written about using markers and fixtures to help you write better tests. So now your project has a high test coverage, and you've caught bug. To investigate, you want to access specific tests with specific parameters. And perhaps you also want to run tests with different parameters without changing your code. So, how do you structure your test to achieve this?

Let's illustrate the solution with an exmaple. You want to create a test with four parameters, A, B, C, and D. Additionally, you have the following requirements:
1. Have default values for each parameter,
2. Specify values for a subset of the parameters if desired (such as via the command line)
3. Use `pytest.mark.parametrize()` to parametrize a subset of parameters

# 1. Adding Custom CLI Options to Pytest
You can extend Pytest's default functionality by adding custom command-line options using the `pytest_addoption` hook. This is particularly useful for customizing tests dynamically without modifying the code.

```py
import pytest

# Add custom CLI options
def pytest_addoption(parser):
    parser.addoption("--A", action="store", default=None, help="stores the given value as string")
    parser.addoption("--B", action="store_const", default=0, help="stores constant value")
    parser.addoption("--C", action="store_true", help="if given, stores True. Otherwise, stores False.")
    parser.addoption("--D", action="store_false", help="if given, stores False. Otherwise, stores True.")

```

`pytest_addoption` is a special "hook function" by Pytest's hook-based plugin system. If hook functions are defined in a test suite, Pytest will discover them and automatically call them during its initialization.

`parser` object is part of the `pytest_addoption`. The `parser.addoption()` method adds new arguments to pytest's CLI. Each argument can have:
* A name (e.g., --A, --B).
* An action (e.g., store saves the argument's value). Unfortunately I honestly could not find documentation that has a list of all the options available.
* A default value used when the argument is not provided.
* A help message displayed in pytest --help.

# 2. Accessing the CLI option values
The `request` object is a built-in pytest fixture that provides information about the test context and configuration. It allows access to command-line options, test parameters, and other runtime data. For example, `request.config.getoption("--OPTION_NAME")` retrieves the value of a custom command-line option defined via `parser.addoption()`.

For example:
```py
@pytest.fixture
def non_parametrized_inputs(request):
    C = request.config.getoption("--C")
    D = request.config.getoption("--D")
    return C, D
```

Here, we use a fixture to define the `non_parametrized_inputs` into our test function.

# 3. Parameterizing Tests and Filtering
Let's define a test function that:

* Uses parameterized inputs (`A` and `B`).
* Filters test cases based on user-specified values of `--A` and `--B`.
* Dynamically uses `--C` and `--D` for customization.

```py
# non_parametrized_inputs() is defined above

# Parameterized test with A and B
@pytest.mark.parametrize("A, B", [
    (1, 2),
    (3, 4),
    (5, 6),
])
def test_function(A, B, non_parametrized_inputs, request):
    # Get custom A and B filters from CLI
    A_filter = request.config.getoption("--A")
    B_filter = request.config.getoption("--B")

    # Skip test cases that don't match the specified A and B
    if A_filter is not None and str(A) != A_filter:
        pytest.skip(f"Skipping A={A}, B={B} because it doesn't match --A={A_filter}")
    if B_filter is not None and str(B) != B_filter:
        pytest.skip(f"Skipping A={A}, B={B} because it doesn't match --B={B_filter}")

    # Get C and D values from the fixture
    C, D = input_values
    print(f"A={A}, B={B}, C={C}, D={D}")

    # Add your test logic here
    assert isinstance(C, str)
    assert isinstance(D, str)
```
Again, `requests` is used to access the CLI inputs.

Key Features of this function:
* Parameterized Inputs:
    * `@pytest.mark.parametrize` generates multiple test cases for `A` and `B`.
* Dynamic Filtering:
    * Users can run specific tests using `--A` and `--B` options.
* Default and Custom Values:
    * `--C` and `--D` allow customization while falling back to defaults when not specified.


# 4. Running Tests: Command-Line Examples
Run All Tests with Defaults:
```bash
pytest -s mytest.py
```
Override C:
```bash
pytest -s mytest.py --C=my_C_value
```
Override C and D:
```bash
pytest -s mytest.py --C=my_C_value --D=my_D_value
```
Run a Specific Test (e.g., A=3 and B=4):
```bash
pytest -s mytest.py --A=3 --B=4
```

# Bonus: Running Tests in the VS Code UI
To execute tests with custom arguments in the VS Code UI:

1. Set Up Pytest in VS Code:

* Open the Command Palette (Ctrl+Shift+P or Cmd+Shift+P on Mac).
* Search for and select Python: Configure Tests.
* Choose pytest and point it to your test directory.

2. Run Tests:

* Use the Testing sidebar (Ctrl+Shift+T or Cmd+Shift+T).
* Click on the test(s) you want to run.

3. Passing Arguments:

Edit the .vscode/settings.json file in your workspace to include Pytest arguments:
```json
{
  "python.testing.pytestArgs": [
    "--A=3",
    "--B=4",
    "--C=my_C_value",
    "--D=my_D_value"
  ]
}
```