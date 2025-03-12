---
layout: post
title:  pytest_generate_tests
categories: [Python,Tutorials, Pytest]
excerpt: Parametrization on crack
---
updated 3/12/2025

As I wrote before, 
* parametrization is preferred over fixtures and `pytest_generate_tests`.
  * `pytest.mark.parametrization()` is simpler and easier to read.
  * If your parameters are fixed, use parametrization
* Use `pytest_generate_tests`-based parametrization when you absolutely know it’s the only way to solve your needs. e.g.,
  * If your parameters need to be generated dynamically -- _but what does this mean?_

## When _not_ to use pytest_generate_tests
Let's look at a toy example:
```py
import pytest

def pytest_generate_tests(metafunc):
    if "input_value" in metafunc.fixturenames:
        metafunc.parametrize("input_value", [1, 2, 3])

def test_example_dynamic_inputs(input_value):
    assert input_value > 0

# functionally equivalent to
@pytest.mark.parametrize("input_value", [1, 2, 3])
def test_example_static_inputs(input_value):
    assert input_value > 0
```
The `pytest_generate_tests` hook is called for each test function in your test suite. It receives a `metafunc` object, which provides information about the test function and allows you to modify it. Specifically, you can use `metafunc` to add parameters to the test function dynamically.

In this example:

`pytest_generate_tests` checks if the test function `test_example` has a parameter named `input_value`.

If it does, `metafunc.parametrize` is used to generate three test cases, each with a different value for `input_value`.

However, this example shows when _not_ to use `pytest_generate_tests`, because the same can be achieved through simple parametrization.

## Use cases for `pytest_generate_tests`
The following examples cannot be achieved via `@pytest.mark.parametrize`:
1. Complex Parameterization: When the parameterization logic is too complex for `@pytest.mark.parametrize`. For example, if you need to generate test cases based on data from a file, database, or API.
   ```py
   def pytest_generate_tests(metafunc):
    if "data" in metafunc.fixturenames:
        data = load_data_from_external_source()  # Load data dynamically
        metafunc.parametrize("data", data)
    ```
2. Conditional Test Generation: When you want to generate tests only under certain conditions, such as based on the environment or configuration.
   ```py
   def pytest_generate_tests(metafunc):
    if "env" in metafunc.fixturenames:
        if os.getenv("TEST_ENV") == "production":
            metafunc.parametrize("env", ["prod"])
        else:
            metafunc.parametrize("env", ["dev", "staging"])
    ```     
3. Dynamic Fixture Creation: When you need to create fixtures dynamically based on the test context.
    ```py
    def pytest_generate_tests(metafunc):
    if "dynamic_fixture" in metafunc.fixturenames:
        metafunc.parametrize("dynamic_fixture", [pytest.fixture(lambda: 42)])
    ```
4. Avoiding Repetition: When you want to avoid repeating the same parameterization logic across multiple test functions.
   ```py
   # conftest.py
   # parametrize all tests requesting "input_value"
   def pytest_generate_tests(metafunc):
    if "input_value" in metafunc.fixturenames:
        metafunc.parametrize("input_value", [1, 2, 3])
    ```

## Example: Dynamic Test Generation Based on External Data
Suppose you have a CSV file with test data, and you want to generate tests dynamically based on the rows in the file:
```py
import csv
import pytest

def load_test_data():
    with open("test_data.csv", "r") as file:
        reader = csv.DictReader(file)
        return [row for row in reader]

def pytest_generate_tests(metafunc):
    if "test_data" in metafunc.fixturenames:
        test_data = load_test_data()
        metafunc.parametrize("test_data", test_data)

def test_data_processing(test_data):
    assert int(test_data["input"]) > 0
```

# Conclusion
`pytest_generate_tests` is a versatile tool for dynamically generating test cases in pytest. It is most appropriate when you need to:

* Parameterize tests dynamically based on external data or complex logic.
* Conditionally generate tests based on the environment or other factors.
* Avoid repetitive parameterization code across multiple test functions.

However, for simpler cases, `@pytest.mark.parametrize` is usually sufficient and more straightforward. Use `pytest_generate_tests` when you need the additional flexibility it provides.
