---
layout: post
title:  Vendoring in Python Packaging
categories: [python, packaging, tutorials, dependency management]
excerpt: Have local or private dependencies? Vendor them into your package.
---

Lately, I've been running into some special cases in Python Packaging. When operating in a monorepo, we often specify other packages in the monorepo as a local dependency. This is fine during development, but issues arise when we try to package and distribute packages with local dependencies.

This issue is becoming more common as monorepos gain popularity, as evidenced by the discussions around this topic:
* "There is no standard mechanism in wheels to handle relative path dependencies" ([source](https://github.com/python-poetry/poetry/issues/4868))
* "Relative paths are problematic. When wheels are being built under PEP-517, the source is expected to be moved into an isolated environment at build time. This means your relative paths will need to hold even when your project source is moved to an ephemeral build directory. ...The general question of 'what should this be relative to?' is still an open question within the packaging group. See [here](https://discuss.python.org/t/what-is-the-correct-interpretation-of-path-based-pep-508-uri-reference/2815) for more on this" ([source](https://github.com/python-poetry/poetry/issues/4868))
* "You should not be able to build the package [containing relative path dependencies], since it is not allowed to have dependencies specified as relative paths in package metadata. PEP 508 only allows version specifiers and URL (which only allows absolute paths even if you use file://)." ([source](https://github.com/pypa/pip/issues/9127))

So what kinds of issues will you encounter?

When you build the package using the Poetry-core backend, it converts your dependency's relative path into an absolute path in the form of `package @ file:///path/to/package`. This information is then written in your package's metadata. However, this path is considered a malformed URL by pip. Installing the built wheel may trigger a `SyntaxError`. I say "may" because it's possible that Poetry 2.x circumvents this issue.

There are [workarounds](https://921kiyo.com/python-packaging-edge-cases/#:~:text=December%2030%2C%202021%204%20minute,by%20Jon%20Cartagena%20on%20Unsplash), but since PEP 508 explicitly disallows local paths in dependency specifications, the optimal solution when packaging such projects is to "vendor" the local dependencies into the project itself.

# What is vendoring?
> Vendoring, in the programming sense, means “copying the source code of another project into your project.” It's in contrast to the practice of using dependencies.

Instead of relying on a package manager to download and install dependencies, vendoring involves manually copying the required libraries into a dedicated directory within your project, typically named `vendor`.

The project's code then imports modules from this local vendor directory.

# When Vendoring is Appropriate:
* Your package relies on local dependencies and other private packages.
* Delivering software to an air-gapped system (lack of access to the package registry). 
* Sometimes you don't want to install anything but the basic interpreter on a computer.
* A dependency is no longer maintained because there are better alternatives now, and it blocks you from upgrading Python. The obvious long-term solution is to rewrite to remove the package, but that’s a major time-consuming task. 
* No additional dependencies/restrictions: For example, your package might introduce dependency A. You need version 1.0.0, and anything earlier/later will break your package. If you don't vendor A in, you need to set A==1.0.0. That might likely break some people's workflow.
* Minimal subset: you might even delete some parts of the package to keep your package small. While file size probably doesn't matter in most cases, automatic code analysis might matter. Also, when you do vulnerability scanning, you might have an easier time telling that you were not affected.
* Breaking changes: you don't need to worry about a dependency introducing breaking changes. That might simplify your tests.
* CI: might run faster.

# When Vendoring is Undesired:
* Maintenance: It's now your code. You need to maintain it.
* Licensing: the vendor's package needs to allow it. You might need to change your package's license.
* Dependency becomes 'hidden'. Hidden dependencies and vendored packages can cause a lot of confusion (like running into a bug that's not present in your version of a lib, but is present in the vendored version). It creates a version coupling that may not have a good reason to exist.
* Increased project size: Vendoring adds the size of the dependencies to your project's repository.
* Potential for divergence: If you modify vendored code, it can become difficult to merge changes with upstream updates.

# How to vendor dependencies into your python package:
Of course, there are other ways to achieve this, and the code snippet below is just an example of a convenience script you can run.

1. Install deps into a directory called vendor
`pip install -r requirements.txt --prefix vendor`

2. Include this code snippet in your program's main module

    ```py
    # This code adds the vendor directory to Python's path so it can find the modules
    import os
    import sys

    parent_dir = os.path.abspath(os.path.dirname(__file__))
    vendor_dir = os.path.join(parent_dir, 'vendor/lib/python3.5/site-packages')
    sys.path.append(vendor_dir)
    ```

source: https://gist.github.com/SeanHood/7901d38772f4eb87151329a26bc07c1b

# Further reading
* [How do you feel about vendored packages?](https://www.reddit.com/r/Python/comments/132jk6l/how_do_you_feel_about_vendored_packages/)
* [What is vendoring?](https://stackoverflow.com/questions/11378921/what-does-the-term-vendoring-or-to-vendor-mean-for-ruby-on-rails)