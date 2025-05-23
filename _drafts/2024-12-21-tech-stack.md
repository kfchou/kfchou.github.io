---
layout: post
title:  My 2025 Tech Stack
categories: [Python, Tech Stack]
---

Other than the obvious Pandas, Numpy, Scipy, Matplotlib, etc...

### Orchestration
* GNU Makefile
* Nox - just like Make, but written in Python

### CLI
* [click](https://github.com/pallets/click/) - simple and fast, low learning curve.
* [Python-Fire](https://github.com/google/python-fire) - a step up from argparse.
* PyTest + `addopts`
* [yaspin](https://github.com/pavdmyt/yaspin) to let me know my program is executing.

### Python and environment Management
* UV - rust-based python version manager.
* Poetry - my preferred package dependency manager, but UV may replace this in the near future. Too many porjects still rely on Poetry and it's unrealistic to expect them to switch over to uv.
  * But there are [workarounds](https://mil.ad/blog/2024/uv-poetry-install.html).

### Testing
* Pytest
* Nox - like GNU Make, but for Python. Use in conjunction with Pytest.

### Static Type Checking
* Pyrefly - Written in Rust by Meta Open Source.

### Profilers
* Scalene - CPU, GPU, and memory profiling all at once. A quick note on interpreting the outputs from Scalene. The goal of optimization would be to:
  - Get as much runtime in native code as possible (C or fortran), in light blue and light green
  - Reduce the number of copying operations to optimize memory usage
  - Sawtooth patterns in timeline with high copy numbers indicate repeated copying and memory consumption
* Memray - Memory profiling.
* cProfiler + SnakeViz - CPU runtime profiling

A note on getting html files in the remote container to render locally

1. Open a simple http server `python3 -m http.server 5500`
2. Under ports in VS Code, forward the port `5500` to some address. e.g., `127.0.0.1:5500`
3. ctrl+click on the forwarded address, or go to [`http://127.0.0.1:5500`](http://127.0.0.1:5500/profile.html) in your browser