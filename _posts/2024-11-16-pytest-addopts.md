---
layout: post
title:  Pytest command line interaction
categories: [Python, Tutorials, virtual environments, pytest]
excerpt: 
---

In the past couple of posts, I've written about using markers and fixtures to help you write better tests. So now your project has a high test coverage, and you've caught bugs. To investigate, you want to access specific tests with specific parameters. And perhaps you also want to run tests with different parameters without changing your code. So, how do you structure your test to achieve this?

Let's illustrate the solution with an exmaple. You want to create a test with four parameters, A, B, C, and D. Additionally, you have the following requirements:
1. Have default values for each parameter,
2. Specify values for a subset of the parameters if desired (such as via the command line)
3. Use `pytest.mark.parametrize()` to parametrize a subset of parameters

Let's see how we can achieve this.

# 1. Adding Custom CLI Options to Pytest
You can extend Pytest's default functionality by adding custom command-line options using the `pytest_addoption` hook. This is particularly useful for customizing tests dynamically without modifying the code.

```py
# contest.py
import pytest

# Add custom CLI options
def pytest_addoption(parser):
    parser.addoption("--A", action="store", default=None, help="stores the given value as string")
    parser.addoption("--B", action="store_const", default=0, const=1, help="stores constant value")
    parser.addoption("--C", action="store_true", help="if given, stores True. Otherwise, stores False.")
    parser.addoption("--D", action="store_false", help="if given, stores False. Otherwise, stores True.")
    parser.addoption("--ALL", action="store_true", help="if given, runs all tests")
```

`pytest_addoption` is a special "hook function" by Pytest's hook-based plugin system. If hook functions are defined in a test suite, Pytest will discover them and automatically call them during its initialization. This hook __must__ be place in `conftest.py` ([docs](https://docs.pytest.org/en/latest/reference/reference.html#_pytest.hookspec.pytest_addoption)).

The `parser` object is part of the `pytest_addoption` hook. The `parser.addoption()` method adds new arguments to pytest's CLI. The syntax used here is equivalent to argparse library’s [add_argument()](https://docs.python.org/3/library/argparse.html#argparse.ArgumentParser.add_argument) function. For example, each argument can have:
* A name (e.g., --A, --B).
* An action (e.g., store saves the argument's value). Unfortunately I honestly could not find documentation that has a list of all the options available.
* A default value used when the argument is not provided.
* A help message displayed in pytest --help.



Note that `store_const` is an action type in argparse (used by pytest) that always assigns a predefined constant value (specified by const) to the option when it is used.

I'll provide a full example in a later section.

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

Here, we use a fixture to define the `non_parametrized_inputs` into our test function. However, _it is not strictly necessary to load the options with a fixture_. In the example below, I load the `--ALL` option directly in my test function.

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
    run_all = request.config.getoption("--ALL")

    if not run_all:
        # Skip test cases that don't match the specified A and B
        if A_filter is not None and str(A) != A_filter:
            pytest.skip(f"Skipping {A=}, {B=} because it doesn't match --A={A_filter}")
        if B_filter is not None and str(B) != str(B_filter):
            pytest.skip(f"Skipping {A=}, {B=} because it doesn't match --B={B_filter}")
        
    # Get C and D values from the fixture
    C, D = non_parametrized_inputs
    print(f"A={A}, B={B}, C={C}, D={D}")
    
    # Add your test logic here
    assert isinstance(C, bool)
    assert isinstance(D, bool)
```
Again, `requests` is used to access the CLI inputs.

Key Features of this function:
* Parameterized Inputs:
    * `@pytest.mark.parametrize` generates multiple test cases for `A` and `B`.
* If the `--ALL` flag is not given, all tests will be skipped unless the filter conditions are satisfied.
* Dynamic Filtering:
    * Users can run specific tests using `--A` and `--B` options. This is equivalent to calling the tests with `pytest mytest.py -k`
* Default and Custom Values:
    * `--C` and `--D` allow customization while falling back to defaults when not specified.


# 4. Running Tests: Command-Line Examples
Run All Tests with Defaults:
```bash
# All tests are skipped due to the test filters
pytest -s mytest.py
```

```bash
# Turn off the filters and run all tests
pytest -s mytest.py --ALL
```

Override C to be True:
```bash
pytest -s mytest.py --C
```

Override C and D:
```bash
pytest -s mytest.py --C --D
```

Run a specific test (e.g., A=3 and B=4):
```bash
pytest -s mytest.py --A=3 --B=4
```

Run a specific parametrized test
```bash
pytest -s mytest.py::test_function[1-2]
```

Run a specific parametrized test with the `k` flag
```bash
# run only the test that matches the call "mytest.py::test_function[3-4]"
pytest -s mytest.py -k 3
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

# Putting it all together
In conclusion, I've demonstrated a few ways to specifify test parameters.
* We use `parser.addoption(--myOption)` to pass in `myOption` from the command line, and retrieve it with `request.config.getoption(--myOption)`.
* Using custom defined filters in combination with `pytest.mark.parametrize` allow us to run multiple or specific tests.
* The built-in pytest filter is the `-k` flag ([docs](https://docs.pytest.org/en/latest/reference/reference.html#command-line-flags)). This is the preferred way to filter specific tests to run. It's usually better to use the `-k` flag rather than using the custom filters if you want to run specific tests.