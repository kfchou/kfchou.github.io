---
layout: post
title:  Testing your code in multiple environments with nox and uv
categories: [Python, Tutorials, Visualizations]
---

1. Install GraphViz
```
sudo apt-get install graphviz
```

2. Install pylint
```
pip install pylint
```

3. Create the class diagram
```
pyreverse -o png -ASmy -c prep.core.raw_data_source.RawDataSource prep
```

`-o` specifies the output format. Pylint will use the GraphViz utility to do the conversion.

All options: https://manpages.ubuntu.com/manpages/trusty/man1/pyreverse.1.html