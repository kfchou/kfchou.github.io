---
layout: post
title:  Pytest Markers & Parametrization
categories: [Python,Tutorials, Pytest]
---

Pytest markers are like tags. Tag your tests to keep them organized. Use markers to indicate test priority, or group them by performance, integration, or acceptance. Use them to skip tests under certain conditions, or mark them as expected failures. Use parametrization to run your test under different parameters.

In this notebook:
- [Common built-in markers](#common-built-in-markers)
  - [Skipping tests (skip)](#skipping-tests-skip)
  - [Expected Failures (xfail)](#expected-failures-xfail)
  - [Specifying Fixtures (usefixtures)](#specifying-fixtures-usefixtures)
  - [Specifying Fixtures (fixtures as input arguments)](#specifying-fixtures-fixtures-as-input-arguments)
  - [Parameterization (Parametrize)](#parameterization-parametrize)
    - [Parametrization pro-tips:](#parametrization-pro-tips)
    - [Use `ids` to make test cases more human-readable](#use-ids-to-make-test-cases-more-human-readable)
    - [Mark Individual parameters](#mark-individual-parameters)
    - [Use dataclasses with Parametrize for complicated args](#use-dataclasses-with-parametrize-for-complicated-args)
- [Custom Markers](#custom-markers)
  - [Tagging Tests](#tagging-tests)
- [Plug-ins required markers:](#plug-ins-required-markers)
  - [Pytest Timeout (timeout)](#pytest-timeout-timeout)
  - [Pytest run order (source)](#pytest-run-order-source)
- [Further Reading](#further-reading)


# Common built-in markers
## Skipping tests (skip)
If you want to skip tests, always state the reason for doing so to provide context for your colleagues and your future self.
```py
import pytest
import sys

# A test that will always be skipped.
@pytest.mark.skip(reason="This test is temporarily disabled.")
def test_example_skip():
    assert 2 + 2 == 4


# A test that will be skipped if it's run on a Python version earlier than 3.8.
@pytest.mark.skipif(sys.version_info < (3, 8), reason="Requires Python 3.8 or later.")
def test_example_skipif():
    assert 3 * 3 == 9
```

## Expected Failures (xfail)
This is very useful when you have a known bug in your code and you want to track it until it’s fixed.

```py
import pytest

# A test that's expected to fail.
@pytest.mark.xfail(reason="Expected to fail until we fix the bug.")
def test_example_xfail():
    assert 2 * 3 == 7

# A normal test that's expected to pass.
def test_example_xpass():
    assert 3 * 2 == 6
```

In pre-production testing, run your tests with `--runxfail` flag. It basically ignores xfail marks.

! important - if you use `skip` and `xfail` marks, you should run your tests with the `-rax` flag to see reasons for skipped tests and expected failures.

## Specifying Fixtures (usefixtures)
Pytest Fixtures help share common test data and logic across multiple tests, reducing code duplication and improving test maintainability.

You can specify which features to use in one of two ways. The first is to decorate the function with `usefixtures("fixture_name")`
```py
import pytest

@pytest.fixture
def database_data():
    return {"username": "Alice", "password": "password123"}

@pytest.mark.usefixtures("database_data")
# Test function using the database_data fixture.
def test_database_entry():
    assert database_data["username"] == "Alice"
    assert database_data["password"] == "password123"
```
This applies the fixture to the test function, ensuring it runs before the test executes.

However, the fixture's return value is not available directly within the test. It's more useful for fixtures that perform setup/teardown tasks but whose return value is not needed.

## Specifying Fixtures (fixtures as input arguments)
The second method is to pass the feature into your test function as an input argument:
```py
import pytest

# A fixture returning a sample database entry.
@pytest.fixture
def database_data():
    return {"username": "Alice", "password": "password123"}


# Test function using the database_data fixture.
def test_database_entry(database_data):
    assert database_data["username"] == "Alice"
    assert database_data["password"] == "password123"

```
The fixture is applied, and its return value (if any) is made available to the test as a parameter.

This is useful when the test needs to directly interact with the fixture's return value.

## Parameterization (Parametrize)
You can run tests multiple times with various parameters via parametrization. For example, the following will generate 3 sets of tests with the given parameters:
```py
import pytest

@pytest.mark.parametrize(
    "test_input,expected", # the input args to parametrize
    [ # the parameters are given as a list of tuples
        (1, 3), 
        (3, 5), 
        (5, 7)
    ])
def test_addition(test_input, expected):
    assert test_input + 2 == expected
```

You can parametrize functions, classes, pytest fixtures. See more examples:
* [pytest-with-eric](https://pytest-with-eric.com/introduction/pytest-parameterized-tests/)

### Parametrization pro-tips:
Some important things to keep in mind:
* Function parametrization is preferred over fixture and pytest_generate_tests.
* Use fixture parametrization if work per parameter is needed.
* Use pytest_generate_tests based parametrization when you absolutely know it’s the only way to solve your needs.
* Utilize `ids` functions to get more human readable parametrized test cases - see [here](#use-ids-to-make-test-cases-more-human-readable).
* Parameters can be marked - see [here](#mark-individual-parameters).
* `@pytest.mark.parametrize` is the simplest way to parametrize your tests. But if you want to use parametrization in combination with the command line, or other more interesting things, see the official docs [here](https://docs.pytest.org/en/stable/example/parametrize.html).

### Use `ids` to make test cases more human-readable
For example, `ids` can be a list of strings:
```py
import pytest

@pytest.mark.parametrize("input,expected", [(1, 2), (3, 4)], ids=["case_1", "case_2"])
def test_add(input, expected):
    assert input + 1 == expected
```
the tests would be named
```bash
test_add[case_1]
test_add[case_2]
```

`ids` can also be callable functions based on the parameter values:
```py
import pytest

def idfn(val):
    return f"input_{val}"

@pytest.mark.parametrize("input,expected", [(1, 2), (3, 4)], ids=idfn)
def test_add(input, expected):
    assert input + 1 == expected
```
which would give:
```bash
test_add[input_1]
test_add[input_3]

```

### Mark Individual parameters
Use `pytest.param()` on individual parameters to mark them:

```py
@pytest.mark.parametrize("a, b, op, expected", [
    pytest.param(1, 2, "+", 3, id= "add"),
    pytest.param(3, 1, "-", 5, id= "sub"),
    pytest.param(2, 3, marks=pytest.mark.xfail, id="xfail_case"),
    pytest.param(3, 4, marks=pytest.mark.skip, id="skip_case"),
    ])
def test_calc(a, b, op, expected):
assert calc(a, b, op) == expected
```

### Use dataclasses with Parametrize for complicated args

Dataclasses help make your test parametrization even more robust:
- Easy setting of test names – could even write a custom
`def __str__(self)`: and use `ids=str`
- Thanks to default arguments, we only need to specify
values that differ from the default (no op="+")
- Better type safety, better autocompletion
- More readability for complex test cases
 
```py
@dataclass
    class CalcCase:
    name: str
    a: int
    b: int
    result: int
    op: str = "+"

@pytest.mark.parametrize("tc", [
    CalcCase("add", a=1, b=2, result=3),
    CalcCase("add-neg", a=-2, b=-3, result=-5),
    CalcCase("sub", a=2, b=1, op="-", result=1),
    ], ids=lambda tc: tc.name)
def test_calc(tc):
    assert calc(tc.a, tc.b, tc.op) == tc.result
```
gives
```
test_calc[add]
test_calc[add-neg]
test_calc[sub]
```
[source](https://github.com/The-Compiler/pytest-tips-and-tricks)


# Custom Markers
Customized markers must be "registered" in `pytest.ini` or `pyproject` for them to be recognized. Examples are provided below.

## Tagging Tests
For example, you can tag tests as "smoke tests" for quick, essential checks, or "regression tests" for a more comprehensive check. Other than registering them in your config file, these "tags" don't need any additional definition to be used.

```py
import pytest

@pytest.mark.smoke
def test_homepage_loads():
    # Test to check if the homepage loads quickly
    assert ...

@pytest.mark.regression
def test_login_successful():
    # Test to check if the login process works as expected
    assert ...

@pytest.mark.regression
def test_user_profile_update():
    # Test to check if user profile updates are saved correctly
    assert ...
```

Register them to your config file:
```toml
# pyproject.toml

[tool.pytest.ini_options]
markers = [
    "smoke: description for smoke",
    "regression: description for regression"
]
```

You can then use markers to run specific types of tests using the -m flag, for instance:

```bash
pytest -m smoke    # Run only smoke tests
pytest -m regression    # Run only regression tests
```

You can mark all tests in a file with `pytestmark`
```py
import pytest
pytestmark = pytest.mark.foo # marks all tests with "foo"
# or
pytestmark = [pytest.mark.foo, pytest.mark.bar, pytest.mark.baz] # apply multiple marks to all tests in this file
```

# Plug-ins required markers:
## Pytest Timeout (timeout)
Specifies a maximum execution time for a test. If the test runs longer than the specified timeout, it’s automatically marked as a failure. This is useful for preventing tests from running indefinitely.
```py
import pytest
import time

# A Slow Running Test that's expected to timeout.
@pytest.mark.timeout(10)
def test_timeout():
    time.sleep(15)
    assert 2 * 3 == 6

```
## Pytest run order ([source](https://github.com/ftobia/pytest-ordering))
Allows you to control the order in which tests are executed. The order argument specifies the relative execution order of tests.
```py
import pytest

@pytest.mark.order2
def test_foo():
    assert True

@pytest.mark.order1
def test_bar():
    assert True
```
Which yields:
```bash
$ py.test test_foo.py -vv
============================= test session starts ==============================
platform darwin -- Python 2.7.5 -- py-1.4.20 -- pytest-2.5.2 -- env/bin/python
plugins: ordering
collected 2 items

test_foo.py:7: test_bar PASSED
test_foo.py:3: test_foo PASSED

=========================== 2 passed in 0.01 seconds ===========================
```
This is a trivial example, but ordering is respected across test files.

# Further Reading
* Tutorial by Florian Bruhin ([pdf](https://github.com/The-Compiler/pytest-tips-and-tricks/blob/main/pytest-tips-and-tricks-ep2024.pdf)) given at PyConDE2024
* Other tutorials by [Florian](https://bruhin.software/#talks-and-trainings)
* A quick summary of pytest markers - [tips and tricks](https://pythontest.com/pytest-tips-tricks/#markers)
* Examples from [pytest-with-eric](https://pytest-with-eric.com/pytest-best-practices/pytest-markers/)
* The official docs on parametrization:
  * [@pytest.mark.parametrize](https://docs.pytest.org/en/7.1.x/how-to/parametrize.html)
  * [Parametrizing tests](https://docs.pytest.org/en/stable/example/parametrize.html)