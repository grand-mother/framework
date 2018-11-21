#!/usr/bin/env python
# -*- coding: utf-8 -*-

import glob
import os
import shutil
import subprocess
import sys
from distutils.core import Command
from setuptools import setup, find_packages


CLASSIFIERS = """\
Development Status :: 3 - Alpha
Intended Audience :: Science/Research
License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)
Programming Language :: Python :: 2.7
Topic :: Scientific/Engineering
Operating System :: POSIX
Operating System :: Unix
Operating System :: MacOS
"""

MAJOR = 0
MINOR = 0
MICRO = 0


def get_root_directory():
    """Return the root directory of the current project"""
    path = os.path.dirname(__file__)
    path = os.path.join(path, "..")
    return os.path.abspath(path)


def get_version():
    """Format the package version"""
    return "{:d}.{:d}.{:d}".format(MAJOR, MINOR, MICRO)


def make_version(package):
    """Build the version.py module for the distribution"""

    version = get_version()

    def system(cmd):
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
        out, _ = p.communicate()
        return out

    if system("git status --porcelain"):
        raise RuntimeError("Dirty git status")

    githash = system("git rev-parse HEAD").strip()

    content = os.linesep.join((
        "# -*- coding: utf-8 -*-",
        "__version__ = \"{:}\"",
        "__githash__ = \"{:}\"")).format(version, githash)

    root = get_root_directory()
    path = os.path.join(root, package, "version.py")
    with open(path, "w+") as f:
        f.write(content)


def parse_meta():
    """Parse some meta data from the README.md"""

    meta = {}
    package_name = None
    with open("README.md", "r") as f:
        for line in f:
            if line.startswith("#"):
                package_name = line[1:].strip().lower().replace(" ", "_")
            elif package_name is not None:
                meta["description"] = line.replace("_", " ").strip()
                break

    if package_name is None:
        raise RuntimeError("Invalid README.md")

    git_name = package_name.replace("_", "-")
    if git_name.startswith("grand-"):
        dist_name = git_name
    else:
        dist_name = "grand-" + git_name
    meta["name"] = dist_name

    return package_name, git_name, meta


class DistClean(Command):
    """Custom clean command, to really clean the repo"""

    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        # Remove build and dist data
        root = get_root_directory()
 
        def remove_directory(dirname):
            path = os.path.join(root, dirname)
            if os.path.exists(path):
                print("removing " + dirname)
                shutil.rmtree(path, ignore_errors=True)

        remove_directory("build")
        remove_directory("dist")
        for path in glob.glob("*.egg-info"):
            remove_directory(path)


def setup_package(clean=False):
    # Parse some top level meta data from the README.md
    package_name, git_name, meta = parse_meta()

    if clean:
        version = get_version() 
    else:
        # Make the version module. Note that this will check the git
        # status as Well
        make_version(package_name)
 
        # Sanity check: import the package
        root = get_root_directory()
        sys.path.append(root)
        package = __import__(package_name)
        version = package.__version__

    # Extra meta data
    meta.update(dict(
        # The author(s) of the package
        author = "The GRAND collaboration",

        # The maintainer(s) of the package, i.e. those who publish it
        maintainer = "GRAND Developers",
        maintainer_email = "grand-dev-l@in2p3.fr",

        # The package description
        version = version,
        url = "https://github.com/grand-mother/" + git_name,
        packages = find_packages(),
        long_description = open("README.md").read(),
        long_description_content_type = "text/markdown",
        include_package_data = True,

        # Meta data can be added here. For a full list of classifiers, see:
        # https://pypi.org/pypi?%3Aaction=list_classifiers
        classifiers = [s for s in CLASSIFIERS.splitlines() if s],

        # Dependencies are declared here together with compatible versions.
        install_requires = "",

        # Executables are registered here
        entry_points = {
            "console_scripts" : (
                "template-executable=template.executable:main",)
        },

        cmdclass = { "distclean" : DistClean }
    ))

    # Call the setup tool
    setup(**meta)


if __name__ == "__main__":
    try:
        command = sys.argv[1]
    except IndexError:
        setup()

    clean = (command == "clean") or (command == "distclean")
    setup_package(clean)
