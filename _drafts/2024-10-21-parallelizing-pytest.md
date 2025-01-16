---
layout: post
title:  Parallelizing Pytest in Github Actions
categories: [Python,Tutorials, Pytest]
---

Setting up pytest on github actions is as simple as having a `.workflow` file that installs pytest and having an action that calls your tests. However, if you have regression tests that take a long time, it is a good idea to parallelize them.

# Matrix strategy
In GitHub Actions, the matrix strategy allows you to run multiple jobs with different configurations in parallel. It is useful for testing across multiple environments, such as different versions of Python, Node, or operating systems.

This exmaple runs tests across 3 operating systems and 3 different python versions for a total of 9 tests.
```
jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]
        python-version: [3.7, 3.8, 3.9]
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v2
        with:
          python-version: ${{ matrix.python-version }}
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run tests
        run: pytest
```

# Using the matrix for your test parameters
You might do something like this to run multiple tests in parallel:
```
jobs:
    regression-tests:
        runs-on: my-server
        strategy:
            matrix:
                test_commands:
                    tests/regression.py --param_1
                    tests/regression.py --param_2
                    tests/regression.py --param_3
                    ...
    steps:
    - name: Checkout repository
      uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v3
      with:
        python-version: '3.10'

    ...

    - name: run tests
      env:
        MY_ENV: "123"
      run:
        pytest -s ${{ github.workspace}}/${{matrix.test_commands}}
```

Using matrix commands have the advantage of
1. Each command is run in parallel by default
2. You can see each individual test command and their results separately in your pull request
3. If one test in the matrix fails, the other will abort
4. You can re-run specific tests in a targeted manner on the Github website.

# Parametrization with Pytest-xdist
THe Matrix command can potentially be inefficient if each test requires setup and takedown steps that can potentially be shared.

The workflow above does the following:
```
- Node 1: Set up -> check out -> install requirements -> run test -> preprocess data -> run test 1
- Node 2: Set up -> check out -> install requirements -> run test -> preprocess data -> run test 2
- Node 3: Set up -> check out -> install requirements -> run test -> preprocess data -> run test 3
```

However, if your test is already parametrized, it may be more desirable to combine the set up procedures to reduce redundancy:
```
- Set up -> check out -> install requirements -> pre-process
    node 1 -> run test 1
    node 2 -> run test 2
    node 3 -> run test 3
```

We want to run the parameterized pytest itself in parallel, and this can be done with `pytest-xdist`.

> ❗If you tests operate on the same resources on your host, you would risk invoking race conditions that can produce unexpected behaviors using this method.

## Installation
```
pip install pytest-xdist
```
## Example test
```
# test_example.py
import pytest

@pytest.mark.parametrize("input,expected", [
    (1, 2),
    (2, 3),
    (3, 4),
    (4, 5)
])
def test_increment(input, expected):
    assert input + 1 == expected
```
Then
```
# Run tests in parallel with 4 CPUs
pytest test_example.py -n 4
```

## `-X` - Abort on the first failure
To mimic the default matrix behavior of aborting tests on the first failure, run the tests with the `-X` flag:
```
# Run tests in parallel with 4 CPUs
pytest test_example.py -n 4 -X
```