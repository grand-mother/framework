# GRAND PKG
_Package manager for GRAND_


## Description

This is a set of utilities for managing and distributing GRAND Python3 packages.
It provides:

- An encapsulation of `setuptools` for building a version controlled package
  that includes GRAND meta data.

- Continuous Integration (CI) tests, both locally, with git hooks, and
  via [GitHub][GITHUB].

- An automatic documentation generation, from docstrings embeded in the source.
  An analysis of the documentation coverage is done at each commit.

#### Command line tools

This utility ships with a set of executables allowing to manage GRAND
packages, as:
```bash
grand-pkg-init [path/to/new/package]
grand-pkg-update [path/to/existing/package]
grand-pkg-config [--edit] [name] [value]
```

#### Web integration

The packages statistics, and their documentation, can be browsed online from
the GRAND [packages pages](https://grand-mother.github.io/site/packages.html).

## Installation

_GRAND packages require python3.7 or later. The package manager can run with
lower version of Python3, though._

#### GRAND package manager

The GRAND package manager uses [pip][PIP] and [PyPi][PYPI] in order to keep
packages up-to-date. Therefore it is recommended to install it to your system
as:
```bash
pip3 install --user grand-pkg
```
Alternatively, the latest commit of this package can be installed directly from
[GitHub][GITHUB], as:

```bash
pip3 install --user git+https://github.com/grand-mother/pkg.git@master
```

Installing binaries to the user space (`--user`) requires the corresponding path
being in your `PATH` environment variable.  Depending on your OS & its version,
this might be already done. If not, you can manually edit your `.bashrc`. The
user space location depends on the OS.  on Linux the path can be updated as:
```bash
export PATH=/home/$(whoami)/.local/bin/:$PATH
```
On OSX use the following:
```bash
export PATH=/users/$(whoami)/Library/Python/3.*/bin/:$PATH
```

#### Python 3.7

On Linux, if not available from your local package manager, you can install
Python3.7 directly from the [tarball](https://www.python.org/downloads) as:
```bash
tar -xvzf Python3.7.*
cd Python3.7.*
make -j4
sudo make -j4 altinstall
```

On OSX Python 3.7 can be installed with brew as:
```bash
brew unlink python
brew install https://raw.githubusercontent.com/Homebrew/homebrew-core/fd8bca8d1cf515bab1da7389afaffec71025cbd3/Formula/python.rb
```
Note that this will install [pip][PIP] as well, a Python package manager. Note
also that in order to use the version 3.7 of python, not the system one (2.7 on
most OS), you must explicitly type `python3` or `pip3`, not `python` or `pip`.

## License

The GRAND software is distributed under the LGPL-3.0 license. See the provided
[`LICENSE`][LICENSE] and [`COPYING.LESSER`][COPYING] files.


[COPYING]: https://github.com/grand-mother/pkg/blob/master/COPYING.LESSER
[GITHUB]: https://github.com/grand-mother/pkg
[LICENSE]: https://github.com/grand-mother/pkg/blob/master/LICENSE
[PIP]: https://pypi.org/project/pip
[PYPI]: https://pypi.org/project/grand-pkg
