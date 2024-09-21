---
layout: post
title:  Pytest pro-tips
categories: [Python,Tutorials, Pytest]
---

A compilation of pro-tips. This page will be periodically updated.

Use plug-ins.
* list of best plug ins ([source](https://pythontest.com/pytest/finding-top-pytest-plugins/))
* [pytest-cov](https://pypi.org/project/pytest-cov/) is consistently on top of the list.

Keeping tests clean:
* One test, one concept
* Aim for a single assertion per test

Make tests human-readable:
* Name tests using the given-when-then convention ([source](https://testdriven.io/tips/0f25ebb7-d5c1-4040-b78e-ac48e8f0a014/))

Doc-tests:
* You can test code examples inside your docstrings like so:
    ```
    $ pytest --doctest-modules http://yourmodule.py
    ```

More tips and tricks:
* [Pythontest.com](https://pythontest.com/pytest-tips-tricks/#markers)
