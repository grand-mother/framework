# -*- coding: utf-8 -*-
"""
Command line interface for managing GRAND packages

Copyright (C) 2018 The GRAND collaboration

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>
"""

import argparse
import editor
import json
import os
import re
import shutil
import subprocess
import sys

from distutils.spawn import find_executable
from setuptools import setup, find_packages
from . import PKG_FILE, PKG_PREFIX
from .hooks import get_top_directory

try:
    input = input
except:
    pass

__all__ = [ "main" ]


_DEFAULT_DESCRIPTION = "Add a brief description"
"""Default description for GRAND packages"""


def _quiet_system(cmd, logger=None):
    """System call with capturing output"""
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE, shell=True)
    out, err = p.communicate()
    if err:
        err = err.decode()
        if logger:
            logger.error(err)
        else:
            return err
    else:
        return out.decode()


def _get_top_directory():
    """Get the user package top directory from git"""
    top = _quiet_system("git rev-parse --show-toplevel")
    if top.startswith("fatal: Not a git repository"):
        return None
    else:
        return top.strip()


def _get_data_dir():
    """Get the absolute path to the package manager data files"""
    path = os.path.dirname(__file__)
    path = os.path.join(path, "data")
    return os.path.abspath(path)


def _copy(data_dir, target_dir, file_, force=False):
    """Copy a file out of the data folder to a target directory"""
    dst = os.path.join(target_dir, file_)
    if force or not os.path.exists(dst):
        src = os.path.join(data_dir, file_)
        shutil.copyfile(src, dst)

def _mkdir(path):
    """Create directories recursively if they don't exist"""
    if not os.path.exists(path):
        os.makedirs(path)


def _write_coverage_config(path, package_name):
    """Write a default config file for `coverage`"""

    content = """\
[run]
branch = True
include = */{:}/*.py

[report]
exclude_lines =
    if self.debug:
    pragma: no cover
    raise NotImplementedError
    except ImportError:
    if __name__ == .__main__.:
ignore_errors = True
omit =
    tests/*
    setup.py
""".format(package_name)

    with open(path, "w") as f:
        f.write(content)


def _write_readme(path, git_name, dist_name, title, description):
    """Write a default README file"""

    content = """\
# {title:}
_{description:}_

## Description

<!-- Add here a description of the package -->


## Installation

_GRAND packages require python3.7. If can be installed from the
[tarball](https://www.python.org/downloads) on Linux or with brew on OSX._

The latest stable version of this package can be installed from [PyPi][PYPI]
using [pip][PIP], e.g. as:
```bash
pip3 install --user {dist_name:}
```

Alternatively one can also install the latest development commit directly from
[GitHub][GITHUB], as:
```bash
pip3 install --user git+https://github.com/grand-mother/{git_name:}.git@master
```


## License

The GRAND software is distributed under the LGPL-3.0 license. See the provided
[`LICENSE`][LICENSE] and [`COPYING.LESSER`][COPYING] files.


[COPYING]: https://github.com/grand-mother/{git_name:}/blob/master/COPYING.LESSER
[GITHUB]: https://github.com/grand-mother/{git_name:}
[LICENSE]: https://github.com/grand-mother/{git_name:}/blob/master/LICENSE
[PIP]: https://pypi.org/project/pip
[PYPI]: https://pypi.org/project/{dist_name:}
""".format(
        title=title, description=description, git_name=git_name,
        dist_name=dist_name)

    with open(path, "w") as f:
        f.write(content)


def _write_source(path, description):
    """Write a default __init__.py file"""

    content = '''\
# -*- coding: utf-8 -*-
"""
{:}

Copyright (C) 2018 The GRAND collaboration

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>
"""

# This is generated by the GRAND package manager in order to track the package
# version. DO NOT DELETE.
try:
    from .version import __version__, __git__
except ImportError:
    __version__ = None
    __git__ = {{}}

# Initialise the package below
'''.format(description)

    with open(path, "w") as f:
        f.write(content)


def _write_setup(path):
    """Write a default setup.py file for the base package"""

    content = """\
# -*- coding: utf-8 -*-

from grand_pkg import setup_package


# The package version
MAJOR = 0
MINOR = 0
MICRO = 0


# Extra package meta data can be added here. For a full list of available
# classifiers, see:
#     https://pypi.org/pypi?%3Aaction=list_classifiers
EXTRA_CLASSIFIERS = (
    "Development Status :: 1 - Planning",
)


if __name__ == "__main__":
    setup_package(
        # Framework arguments
        __file__, (MAJOR, MINOR, MICRO), EXTRA_CLASSIFIERS,

        # Vanilla setuptools.setup arguments can be added below,
        # e.g. `entry_points` for executables or `data_files`
    )
"""

    with open(path, "w") as f:
        f.write(content)


def _write_tests_init(path, package_name):
    """Write a default __init__.py file for the tests package"""

    content = '''\
# -*- coding: utf-8 -*-
"""
Unit tests for the {:} package
"""
'''.format(package_name)

    with open(path, "w") as f:
        f.write(content)


def _write_tests_main(path, package_name):
    """Write a default __main__.py file for the tests package"""

    content = '''\
# -*- coding: utf-8 -*-
"""
Run all unit tests for the {:} package
"""
import os
import unittest
import sys


def suite():
    test_loader = unittest.TestLoader()
    path = os.path.dirname(__file__)
    test_suite = test_loader.discover(path, pattern="test_*.py")
    return test_suite


if __name__ == "__main__":
    runner = unittest.TextTestRunner(verbosity=2)
    r = not runner.run(suite()).wasSuccessful()
    sys.exit(r)
'''.format(package_name)

    with open(path, "w") as f:
        f.write(content)


def _write_tests_version(path, package_name):
    """Write a default test_version.py file for the tests package"""

    content = '''\
# -*- coding: utf-8 -*-
"""
Unit tests for the {0:}.version module
"""

import unittest
import sys

import {0:}
from grand_pkg import git


try:
    import {0:}.version
except:
    # Skip version tests for non release builds
    pass
else:
    class VersionTest(unittest.TestCase):
        """Unit tests for the version module"""

        def test_hash(self):
            githash = git("rev-parse", "HEAD")
            self.assertEqual(githash.strip(), {0:}.version.__git__["sha1"])

        def test_version(self):
            self.assertIsNotNone({0:}.version.__version__)


if __name__ == "__main__":
    unittest.main()
'''.format(package_name)

    with open(path, "w") as f:
        f.write(content)


def _add_git_hook(git_dir, hook_name):
    """Add a hook for managing git workflow"""

    exe_name = PKG_PREFIX + hook_name
    exe_path = find_executable(exe_name)
    if not exe_path:
        msg = ( "Warning: could not locate " + exe_name,
                "  Hook has not been installed",
                "")
        sys.stderr.write(os.linesep.join(msg))
        return False

    path = os.path.join(git_dir, "hooks", hook_name)
    try:
        os.remove(path)
    except OSError:
        pass
    os.symlink(exe_path, path)
    return True


def _parse_readme(package_dir):
    """Parse some meta data from the README.md"""

    path = os.path.join(package_dir, "docs/README.md")
    meta = {"description": _DEFAULT_DESCRIPTION}
    package_name = None
    with open(path, "r") as f:
        for line in f:
            if line.startswith("#"):
                package_name = line[1:].strip().lower().replace(" ", "_")
            elif package_name is not None:
                meta["description"] = line.replace("_", " ").strip()
                break

    if package_name is None:
        return None

    git_name = package_name.replace("_", "-")
    if git_name.startswith("grand-"):
        dist_name = git_name
    else:
        dist_name = "grand-" + git_name

    meta["name"] = package_name
    meta["git-name"] = git_name
    meta["dist-name"] = dist_name

    return meta


class _Logger:
    """Utility class for logging"""

    def __init__(self, quiet):
        self.quiet = quiet

    def info(self, msg, *args, exit=False):
        if not self.quiet:
            if args:
                msg = msg.format(*args)
            print(msg)
        if exit:
            sys.exit(0)

    def error(self, msg, *args, exit=True):
        if not self.quiet:
            if args:
                msg = msg.format(*args)
            print(msg, file=sys.stderr)
        if exit:
            sys.exit(1)
        else:
            return False


def init(args=None):
    """Initialise a bare GRAND package"""

    parser = argparse.ArgumentParser(
        description='Initialise a bare GRAND package.')
    parser.add_argument(
        "path", type = str, nargs = "?", default = ".",
        help = "the path to the package")
    parser.add_argument(
        "-d", "--default", dest = "use_default", action = "store_const",
        const = True, default = False, help = "use default options")
    parser.add_argument(
        "-q", "--quiet", dest = "quiet", action = "store_const",
        const = True, default = False, help = "suppress any output")
    args = parser.parse_args(args)

    # Instanciate a logger
    logger = _Logger(args.quiet)

    # Set system calls
    system = _quiet_system if args.quiet else os.system

    # Path to the package data
    data_dir = _get_data_dir()

    # Set the package top directory
    package_dir = os.path.abspath(args.path)
    if os.path.exists(package_dir):
        path = os.path.join(package_dir, PKG_FILE)
        if os.path.exists(path):
            logger.error("Package already exists ...")
    else:
        _mkdir(package_dir)

    # Add static file, e.g. licensing
    _copy(data_dir, package_dir, "LICENSE", force=True)
    _copy(data_dir, package_dir, "COPYING.LESSER", force=True)
    _copy(data_dir, package_dir, "MANIFEST.in")
    _copy(data_dir, package_dir, ".gitignore")
    _copy(data_dir, package_dir, ".travis.yml", force=True)

    # Initialise the docs
    docs_dir = os.path.join(package_dir, "docs")
    _mkdir(docs_dir)

    # Get the package name from any existing source
    packages = find_packages(package_dir, exclude=("tests",))
    if len(packages) == 1:
        default_name = packages[0].lower()
    else:
        default_name = os.path.basename(package_dir).replace("-", "_").lower()

    # Prompt the package meta data
    if args.use_default:
        package_name = default_name
    else:
        prompt = "Please enter the package name [{:}]: ".format(
            default_name)
        package_name = input(prompt).strip()
        if not package_name:
            package_name = default_name

    if not package_name:
        logger.info("Aborting ...", exit=True)
    elif not re.match(r'^[a-z][a-z0-9_]*$', package_name):
        logger.error("Invalid package name (PEP8) ...")

    if args.use_default:
        description = _DEFAULT_DESCRIPTION
    else:
        prompt = "Please enter a brief description: "
        description = input(prompt).strip()
        if not description:
            description = _DEFAULT_DESCRIPTION

    git_name = package_name.replace("_", "-")
    if git_name.startswith("grand-"):
        dist_name = git_name
    else:
        dist_name = "grand-" + git_name

    # Write a default README
    path = os.path.join(docs_dir, "README.md")
    if not os.path.exists(path):
        title = package_name.replace("_", " ").replace("-", " ").capitalize()
        _write_readme(path, git_name, dist_name, title, description)

    # Write the configuration file for `coverage`
    path = os.path.join(package_dir, ".coveragerc")
    if not os.path.exists(path):
        _write_coverage_config(path, package_name)

    # Initialise the source
    src_dir = os.path.join(package_dir, package_name)
    _mkdir(src_dir)

    path = os.path.join(src_dir, "__init__.py")
    if not os.path.exists(path):
        _write_source(path, description)

    # Initialise (or update) the tests
    tests_dir = os.path.join(package_dir, "tests")
    _mkdir(tests_dir)

    path = os.path.join(tests_dir, "__init__.py")
    if not os.path.exists(path):
        _write_tests_init(path, package_name)

    path = os.path.join(tests_dir, "__main__.py")
    _write_tests_main(path, package_name)

    path = os.path.join(tests_dir, "test_version.py")
    _write_tests_version(path, package_name)

    # Initialise the setup script
    path = os.path.join(package_dir, "setup.py")
    if not os.path.exists(path):
        _write_setup(path)

    # Initialise git
    git_dir = os.path.join(package_dir, ".git")
    if not os.path.exists(git_dir):
        system("git init " + package_dir)
        commit = True
    else:
        commit = False

    # Add hooks for git
    code = 0
    if not _add_git_hook(git_dir, "pre-commit"): code = 1
    if not _add_git_hook(git_dir, "prepare-commit-msg"): code = 1

    # Dump the initial stats.
    path = os.path.join(package_dir, PKG_FILE)
    if not os.path.exists(path):
        with open(path, "w") as f:
            json.dump({"package": {"name": package_name, "git-name": git_name,
                                   "dist-name": dist_name,
                                   "description": description}}, f)

    # Do the initial commit
    if commit:
        command = ["cd " + package_dir]
        files = (
            ".coveragerc", ".gitignore", ".travis.yml", "COPYING.LESSER",
            "LICENSE", "MANIFEST.in", "docs/README.md", "setup.py", "tests",
            package_name
        )
        for file_ in files:
            command.append("git add " + file_)
        command.append("git commit -m 'Initial commit'")
        system(" && ".join(command))

    # Exit to the OS
    sys.exit(code)


def update(args=None):
    """Update a GRAND package"""

    parser = argparse.ArgumentParser(
        description='Update a GRAND package.')
    parser.add_argument(
        "path", type = str, nargs = "?", default = "",
        help = "the path to the package")
    parser.add_argument(
        "-q", "--quiet", dest = "quiet", action = "store_const",
        const = True, default = False, help = "suppress any output")
    args = parser.parse_args(args)

    # Instanciate a logger
    logger = _Logger(args.quiet)

    # Set system calls
    def system(cmd):
        return _quiet_system(cmd, logger)

    # Check for an update
    user = "" if hasattr(sys, "real_prefix") else "--user" # Hack for virtualenv
    out = system("pip3 install {:} --upgrade grand-pkg".format(user))
    if not out.startswith("Requirement already up-to-date: grand-pkg"):
        logger.info(out)

    # Set the package top directory
    if args.path:
        package_dir = os.path.abspath(args.path)
    else:
        package_dir = _get_top_directory()
        if package_dir is None:
            logger.error("Not a GRAND package ...")

    update_data = False
    if os.path.exists(package_dir):
        path = os.path.join(package_dir, PKG_FILE)
        if not os.path.exists(path):
            update_data = True
            path = os.path.join(package_dir, ".stats.json")
            if not os.path.exists(path):
                logger.error("Not a GRAND package ...")
    else:
        logger.error("Path does not exist ...")

    # Update static files, e.g. licensing
    data_dir = _get_data_dir()

    _copy(data_dir, package_dir, "LICENSE", force=True)
    _copy(data_dir, package_dir, "COPYING.LESSER", force=True)
    _copy(data_dir, package_dir, ".travis.yml", force=True)

    # Update the hooks for git
    git_dir = os.path.join(package_dir, ".git")
    code = 0
    if not _add_git_hook(git_dir, "pre-commit"): code = 1
    if not _add_git_hook(git_dir, "prepare-commit-msg"): code = 1

    # Check for old style meta
    with open(path, "r") as f:
        stats = json.load(f)

    if not "package" in stats:
        meta = _parse_readme(package_dir)
        if meta is None:
            logger.error("Could not parse package data from the README ...")
        update_data = True
        stats["package"] = meta

    if update_data:
        old_path = os.path.join(package_dir, ".stats.json")
        if os.path.exists(old_path):
            system("git mv .stats.json " + PKG_FILE)
        path = os.path.join(package_dir, PKG_FILE)
        with open(path, "w") as f:
            json.dump(stats, f)
        system("git add " + PKG_FILE)

        # Update the setup file and the tests
        path = os.path.join(package_dir, "setup.py")
        _write_setup(package_dir)

        tests_dir = os.path.join(package_dir, "tests")
        path = os.path.join(tests_dir, "__init__.py")
        _write_tests_init(path, package_name)

        path = os.path.join(tests_dir, "__main__.py")
        _write_tests_main(path, package_name)

        path = os.path.join(tests_dir, "test_version.py")
        _write_tests_version(path, package_name)

    # Exit to the OS
    sys.exit(code)


def config(args=None):
    """Manage the configurable data of a GRAND package"""

    parser = argparse.ArgumentParser(
        description='Manage the configurable data of a GRAND package.')
    parser.add_argument(
        "name", type = str, nargs = "?", default = "",
        help = "the parameter name")
    parser.add_argument(
        "value", type = str, nargs = "?", default = "",
        help = "the value to set")
    parser.add_argument(
        "-e", "--edit", dest = "edit", action = "store_const",
        const = True, default = False, help = "open an editor")
    parser.add_argument(
        "-q", "--quiet", dest = "quiet", action = "store_const",
        const = True, default = False, help = "suppress any output")
    args = parser.parse_args(args)

    # Instanciate a logger
    logger = _Logger(args.quiet)

    # Load the current data
    package_dir = _get_top_directory()
    if (package_dir is None) or not os.path.exists(package_dir):
        logger.error("Not a GRAND package ...")
    else:
        path = os.path.join(package_dir, PKG_FILE)
        if not os.path.exists(path):
            logger.error("Not a GRAND package ...")

    with open(path, "r") as f:
        pkg_data = json.load(f)

    def check_meta(obj):
        for name, value in obj.items():
            if name == "name":
                if not re.match(r'^[a-z][a-z0-9_]*$', value):
                    return logger.error("Invalid package name: `{}' ...",
                                        value, exit=False)
            elif (name == "git-name") or (name == "dist-name"):
                if not re.match(r'^[a-z][a-z0-9-]*$', value):
                    return logger.error("Invalid {}: `{}' ...",
                                        name.replace("-", " "), value,
                                        exit=False)
            elif name != "description":
                return logger.error("Invalid parameter `{}' ...", name)
        return True

    if not args.edit:
        if not args.name:
            logger.info(json.dumps(pkg_data["package"],
                                   sort_keys=True, indent=4))
            sys.exit(0)
        elif not args.value:
            # Print the parameter value
            if not args.name in pkg_data["package"]:
                logger.error("Invalid parameter `{}' ...", args.name)
            else:
                logger.info(pkg_data["package"][args.name], exit=True)
        else:
            # Update the parameter value
            obj = { args.name: args.value }
            if not check_meta(obj):
                sys.exit(1)
    else:
        # Spawn an editor
        txt = json.dumps(pkg_data["package"], sort_keys=True, indent=4)
        while True:
            txt = editor.edit(contents=txt.encode(), suffix=".json").decode()
            try:
                obj = json.loads(txt)
            except Exception as e:
                if args.quiet:
                    sys.exit(1)
                logger.info("Invalid JSON format ...")
                logger.info(e)
            else:
                # Check the result
                if check_meta(obj):
                    break

            # Invalid data. Shall we abort?
            while True:
                key = input("Continue editing? ([y]/n): ")
                if key == "n":
                    sys.exit(1)
                elif (key == "") or (key == "y"):
                    break

    # Update the package data
    d = pkg_data["package"]
    before = hash(json.dumps(d))
    d.update(obj)
    if hash(json.dumps(d)) == before:
        sys.exit(0)

    # Dump the updated data
    with open(path, "w") as f:
        json.dump(pkg_data, f)

    system = _quiet_system if args.quiet else os.system
    system("git add " + PKG_FILE)
    sys.exit(0)


if __name__ == "__main__":
    # Get the function to call from the command line
    ret = globals()[sys.argv[1]](sys.argv[2:])
    if ret is not None:
        print(ret)
