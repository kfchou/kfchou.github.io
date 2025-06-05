---
layout: post
title:  Vendoring in Python Packaging
categories: [python, packaging, tutorials, dependency management]
excerpt: Have local, private dependencies? Vendor them into your package.
---

# What is vendoring?
> Vendoring, in the programming sense, means “copying the source code of another project into your project.” It's in contrast to the practice of using dependencies.

Instead of relying on a package manager to download and install dependencies, vendoring involves manually copying the required libraries into a dedicated directory within your project, typically named `vendor`.

The project's code then imports modules from this local vendor directory.

# When Vendoring is Appropriate:
* Your package relies on local dependencies and other private packages.
* Delivering software to an air-gapped system (lack of access to the package registry). 
* Sometime you don't want install anything but basic interpreter on a computer.
* A dependency is no longer maintained, because there’s better alternatives now and it blocks you from upgrading Python. The obvious long term solution is to rewrite to remove the package, but that’s a major time-conuming task. 
* No additional dependencies / restrictions: For example, your package might introduce dependency A. You need version 1.0.0 and anything earlier / later will break your package. If you don't vendor A in, you need to set A==1.0.0. That might likely break some people's workflow.
* Minimal subset: you might even delete some parts of the package to keep your package small. While file size probably doesn't matter in most cases, automatic code analysis might matter. Also when you do vulnerability scanning you might have an easier time to tell that you were not affected.
* Breaking changes: you don't need to worry about a dependency introducing breaking changes. That might simplify your tests
* CI: might run faster

# When Vendoring is Undesired:
* Maintenance: It's now your code. You need to maintain it.
* Licensing: the vendors package needs to allow it. You might need to change your packages license.
* Dependency becomes 'hidden'. Hidden dependencies and vendored packages can cause a lot of confusion (like running into a bug that's not present in your version of a lib, but is present in the vendored version). It creates a version coupling that may not have a good reason to exist.
* Increased project size: Vendoring adds the size of the dependencies to your project's repository.
* Potential for divergence: If you modify vendored code, it can become difficult to merge changes with upstream updates.

# IRL Vendoring examples:
`Requests` is a popular package that used to vendor some packages: urllib3, chardet, and idna. But it caused some issues and was removed. You can read about some of the issues in [8e17600](https://github.com/psf/requests/commit/8e17600ef60de4faf632acb55d15cb3c178de9bb#diff-3ad3ee27adeec190ba56ee51b89a8cff69d5f700fae48fecfa4cd90ee84b62c4) (expand the deleted requests/packages/__init__.py for the scoop).

# How to vendor in python packages:
1. Install deps into a directory called vendor
`pip install -r requirements.txt --prefix vendor`

2. Include this code snipped in your program's main module
```py
# This code adds the vendor directory to Python's path so it can find the modules
import os
import sys

parent_dir = os.path.abspath(os.path.dirname(__file__))
vendor_dir = os.path.join(parent_dir, 'vendor/lib/python3.5/site-packages')
sys.path.append(vendor_dir)
```
source: https://gist.github.com/SeanHood/7901d38772f4eb87151329a26bc07c1b

Sources:
* https://www.reddit.com/r/Python/comments/132jk6l/how_do_you_feel_about_vendored_packages/
* https://stackoverflow.com/questions/11378921/what-does-the-term-vendoring-or-to-vendor-mean-for-ruby-on-rails