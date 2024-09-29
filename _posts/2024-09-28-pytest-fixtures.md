---
layout: post
title:  Pytest Fixtures
categories: [Python,Tutorials, Pytest]
---
Fixtures in pytest are functions that provide a fixed baseline for tests, allowing resources (like database connections, input data, etc.) to be accessed and reused across multiple test cases. They can also handle setup and teardown for each test.
Upon test initialization, fixtures are executed, and their results cached to be used and reused. The persistence of this cache depends on a specified "scope". In this note, my intention is to jot down important concepts about fixtures and show some common ways in which they're used.

In this note:
- [Default Fixtures](#default-fixtures)
- [Requesting Fixtures](#requesting-fixtures)
- [Autouse fixtures](#autouse-fixtures)
- [Fixture Scopes](#fixture-scopes)
- [Conftest file](#conftest-file)
- [The `request` fixture](#the-request-fixture)
  - [Example: Using requests with parametrized tests](#example-using-requests-with-parametrized-tests)
- [Fixtures from third-party plugins](#fixtures-from-third-party-plugins)
- [Fixture instantiation order](#fixture-instantiation-order)
- [Additional Resources](#additional-resources)


# Default Fixtures
Pytest has a bunch of useful built-in fixtures, made available during all tests. The most common ones include:
* tmpdir: Provides a temporary directory as a py.path.local object for file operations during a test. The directory is automatically cleaned up after the test.
* tmp_path: Provides a temporary directory as a pathlib.Path object, offering modern path handling.
* monkeypatch: Allows you to modify or override attributes, environment variables, or functions during a test. This is useful for isolating and controlling the test environment.
* recwarn: Captures warnings issued during the test, allowing you to assert that a particular warning was raised.
* caplog: Captures log messages for testing purposes. Useful for verifying that certain log messages are produced during execution.
* [request](#the-request-fixture): Provides access to information about the requesting test, such as its name, scope, and fixture dependencies. It is particularly useful for parameterized or dynamically controlled fixtures.

See the full list [here](https://docs.pytest.org/en/stable/reference/fixtures.html)

# Requesting Fixtures
A test can "request" fixtures to access the shared resource.

To do this, pass fixtures into the test function as a parameter:
```py
import pytest

@pytest.fixture
def sample_data():
    return {"name": "John", "age": 30}

def test_data_usage(sample_data):
    assert sample_data["name"] == "John"
    assert sample_data["age"] == 30
```

Here, sample_data is a fixture that can be used in multiple test functions, reducing redundancy. Our function
`test_data_usage` requests `sample_data` via its positional argument. If a fixture is in a test function argument:
1. pytest executes the fixture function `sample_data`
2. whatever `sample_data` returns is passed into `test_data_usage` as an argument

Some things to know
* Fixtures can request other fixtures
* Fixtures are reusable (by functions and fixtures)
* Tests and fixtures can request more than one fixture at a time

# Autouse fixtures
Sometimes you may want to have a fixture (or even several) that you know all your tests will depend on. "Autouse" fixtures are a convenient way to make all tests automatically request them.

Here's a practical example:
```py
import pytest

@pytest.fixture(autouse=True)
def setup_teardown():
    # Code executed before each test. e.g., create a test user
    print("\nSetup code")

    yield  # Control is handed to the test function

    # Code executed after each test. e.g., delete the test user
    print("Teardown code")

def test_one():
    print("Executing test_one")
    assert True

def test_two():
    print("Executing test_two")
    assert True
```

These tests would output
```
Setup code
Executing test_one
Teardown code

Setup code
Executing test_two
Teardown code
```
This is useful for common setup or teardown code that should run for every test, like initializing configurations or cleaning up resources.

Some common use cases may include:
* **Global Setup or Teardown Requirements**: Logging, clearing cache, or setting environment variables
* **Side Effects for All Tests**: Example: Starting a test server or applying database migrations before running tests.
* **State or Environment Configuration**: Temporarily changing environment vars for a set of tests
* **Resetting External Resources**: Removing all entries from a test database, flushing a queue, or resetting an API state.

# Fixture Scopes
Using `scopes`, we can control whether a fixture should be available across functions, classes, modules, packages, or the entire session:
```py
@pytest.fixture(scope="module")
```

Possible values for `scope` are:
* `function` - (default) the fixture is destroyed at the end of the test
* `class` - the fixture is destroyed during teardown of the last test in the class
* `module` - the fixture is destroyed during teardown of the last test in the module
* `package` -  the fixture is destroyed during teardown of the last test in the package where the fixture is defined, including sub-packages and sub-directories within it
* or `session` - the fixture is destroyed at the end of the test session

For example, fixtures requiring network access depend on connectivity and are usually time-expensive to create. We can add a `scope="module"` parameter to the `@pytest.fixture` invocation to cause a `smtp_connection` fixture function, responsible to create a connection to a preexisting SMTP server, to only be invoked once per test module (the default is to invoke once per test function). Multiple test functions in a test module will thus each receive the same `smtp_connection` fixture instance, thus saving time.

Pytest only caches one instance of a fixture at a time, which means that when using a parametrized fixture, pytest may invoke a fixture more than once in the given scope.

# Conftest file
The conftest.py file in pytest is a special configuration file used to define fixtures, hooks, and plugins that should be shared across multiple test modules *without needing to import them explicitly*. It serves as a centralized place for test configuration and is automatically discovered by pytest.

Fixtures defined in conftest.py can be used across different test files within the **same directory or its subdirectories**.
```py
# conftest.py
import pytest

@pytest.fixture
def common_fixture():
    return "Common fixture for all tests"
```
Test files can directly use common_fixture **without needing to import it**:
```py
# test_example.py
def test_using_common_fixture(common_fixture):
    assert common_fixture == "Common fixture for all tests"
```
Common uses:
* Define global test fixtures that should be available across multiple test modules.
* Implement custom hooks that modify pytest behavior.
* Ensure consistency across test modules without redundant imports or fixture definitions.

# The `request` fixture 
Fixtures can introspect the requesting test context via the `request` fixture.

The `request` fixture gets you access to a `FixtureRequest` instance. It is made available and injected manually by pytest for every test. It is used for accessing some pytest internals, in cases where you want to do something dynamic with pytest.

Fixture functions can accept the `request` object to introspect the "requesting" test function, class or module context.

```py
# content of conftest.py
import smtplib
import pytest

@pytest.fixture(scope="module")
def smtp_connection(request):
    server = getattr(request.module, "smtpserver", "smtp.gmail.com")
    smtp_connection = smtplib.SMTP(server, 587, timeout=5)
    yield smtp_connection
    print(f"finalizing {smtp_connection} ({server})")
    smtp_connection.close()
```
```py
# content of test_anothersmtp.py
smtpserver = "mail.python.org"  # will be read by smtp fixture

def test_showhelo(smtp_connection):
    assert 0, smtp_connection.helo()
```
Here, `request.module` can access the namespace of the module from which the request was made. In this case, it would be able to access the namespace of `test_anothersmtp.py`.

Using the request object, a fixture can access...
* The test function that is currently using the fixture, including its name, parameters, and docstring
* Markers which are applied to a test function
* Metadata and Test Parameters (for parametrized tests)
* and a whole slew of other things - see the [docs](https://docs.pytest.org/en/stable/reference/reference.html#request)

## Example: Using requests with parametrized tests
To request a fixture in a parameterized test, you need to use the `indirect=True` parameter in `@pytest.mark.parametrize`. This tells pytest to pass the parameter to the fixture rather than directly to the test function, allowing you to use the fixture logic for each parameter value.

Suppose you have a fixture that sets up some resource based on the parameter value:
```py
import pytest

@pytest.fixture
def setup_data(request):
    # Access the parameter value through request.param
    param_value = request.param
    
    # Do something with the parameter value
    return f"Setup data with parameter: {param_value}"

# Use @pytest.mark.parametrize with indirect=True to pass the parameter to the fixture
@pytest.mark.parametrize("setup_data", ["value1", "value2", "value3"], indirect=True)
def test_using_parametrized_fixture(setup_data):
    assert setup_data in ["Setup data with parameter: value1",
                          "Setup data with parameter: value2",
                          "Setup data with parameter: value3"]
```
* The decorator `@pytest.mark.parametrize("setup_data", ["value1", "value2", "value3"], indirect=True)` indicates that the values `"value1"`, `"value2"`, `"value3"` should be passed to the fixture `setup_data`
* The `indirect=True` argument tells pytest to treat `"setup_data"` as the fixture and pass the parameter values to it instead of directly to the test function.

This approach allows you to leverage fixtures dynamically with different parameters in a clean and maintainable way.

# Fixtures from third-party plugins
Many pytest plugins operate by providing fixtures. As long as those plugins are installed, the fixtures they provide can be requested from anywhere in your test suite. Due tot he Pytest discovery mechanism, it will discover fixtures provided by plugins *last*, after all other fixtures are discovered.

# Fixture instantiation order
See the [official docs](https://docs.pytest.org/en/stable/reference/fixtures.html#fixture-instantiation-order) on this one.

# Additional Resources
* Fixture availabillity and instantiation order ([official docs](https://docs.pytest.org/en/stable/reference/fixtures.html#))
* Lots of examples on how they're used from the [official docs](https://docs.pytest.org/en/stable/how-to/fixtures.html)