<!--
    This file is auto generated by the GRAND framework.
    Beware: any change to this file will be overwritten at next commit.
    One should edit the docs/README.md file instead.
-->

[![Coding style](https://img.shields.io/badge/pep8-89%25-brightgreen.svg)](https://github.com/grand-mother/framework/blob/master/docs/.stats.json)
[![Code coverage](https://codecov.io/gh/grand-mother/framework/branch/master/graph/badge.svg)](https://codecov.io/gh/grand-mother/framework)
[![Build status](https://travis-ci.com/grand-mother/framework.svg?branch=master)](https://travis-ci.com/grand-mother/framework)
[![Documentation](https://img.shields.io/badge/docs-48%25-yellow.svg)](https://grand-mother.github.io/site/reports.html?framework/docs)
[![PyPi version](https://img.shields.io/pypi/v/g.svg)](https://pypi.org/project/grand-framework)

# Framework
_Common framework for GRAND packages_


## Description

This is a set of utilities for managing and distributing GRAND Python3 packages
within a common _standard_ framework. It provides:

- An encapsulation of `setuptools` for building a version controlled package
  that includes GRAND meta data.

- Continuous Integration (CI) tests, both locally, with git hooks, and
  via [GitHub][GITHUB].

- An automatic documentation generation, from docstrings embeded in the source.
  An analysis of the documentation coverage is done at each commit.

#### Command line tools

This utility ships with an executable, `grand-pkg-init`, which allows to create
~~or convert~~ an existing GRAND package, as:
```bash
grand-pkg-init path/to/package
```
Then, you might need to answer a few questions in order to configure the GRAND
package.

#### Web integration

The packages statistics, and their documentation, can be browsed online from
the GRAND [packages pages](https://grand-mother.github.io/site/packages.html).

## Installation

#### Installation of Python3.7

GRAND packages are based on python3.7. On Linux you can install it from the
[tarball](https://www.python.org/downloads) as:
```bash
tar -xvzf Python3.7.2
cd Python3.7.2
make -j4
sudo make -j4 altinstall
```
On OSX Python 3.7 can be installed with brew as:
```bash
brew unlink python
brew install https://raw.githubusercontent.com/Homebrew/homebrew-core/fd8bca8d1cf515bab1da7389afaffec71025cbd3/Formula/python.rb
```
Note that this will install [pip][PIP] as well, a Python package manager. Note
also that in order to use the version 3.7 of python, not the system one, you
must explicitly type `python3.7` or `pip3.7`, not `python`.

#### Installation of the frawmework

Once you have Python3.7 (and pip), the latest commit of this package can
be installed from [GitHub][GITHUB], as:
```bash
pip3.7 install --user git+https://github.com/grand-mother/framework.git@master
```
Installing the package to the user space (`--user`) requires adding the
corresponding path to your `PATH` and `PYTHONPATH` environment variables. This
can be done, e.g. in the `.bashrc`. The user space location depends on the OS.
on Linux the path can be updated as:
```bash
export PYTHONPATH=/home/$(whoami)/.local/lib/python3.7/site-packages/:$PYTHONPATH
export PATH=/home/$(whoami)/.local/bin/:$PATH
```
On OSX use the following:
```bash
export PYTHONPATH=/users/$(whoami)/Library/Python/3.7/lib/site-packages/:$PYTHONPATH
export PATH=/users/$(whoami)/Library/Python/3.7/bin/:$PATH
```

Note that the framework is not yet registered to [PyPi][PYPI]. Otherwise, it
could have been installed with [pip][PIP] as well, e.g. as:
```bash
pip3.7 install --user grand-framework
```

## License

The GRAND software is distributed under the LGPL-3.0 license. See the provided
[`LICENSE`][LICENSE] and [`COPYING.LESSER`][COPYING] files.


[COPYING]: https://github.com/grand-mother/framework/blob/master/COPYING.LESSER
[GITHUB]: https://github.com/grand-mother/framework
[LICENSE]: https://github.com/grand-mother/framework/blob/master/LICENSE
[PIP]: https://pypi.org/project/pip
[PYPI]: https://pypi.org/project/grand-framework
