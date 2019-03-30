# -*- coding: utf-8 -*-

import os
from framework import PKG_PREFIX, setup_package


# The package version
MAJOR = 0
MINOR = 1
MICRO = 0


# Extra package meta data can be added here. For a full list of available
# classifiers, see:
#     https://pypi.org/pypi?%3Aaction=list_classifiers
EXTRA_CLASSIFIERS = (
    "Development Status :: 4 - Beta",
    "Programming Language :: Python :: 3.5"
    "Programming Language :: Python :: 3.6"
)


def main():
    setup_package(
        # Framework arguments
        __file__, (MAJOR, MINOR, MICRO), EXTRA_CLASSIFIERS,

        # Vanilla setuptools.setup arguments
        install_requires = (
            "astor>=0.7.1",
            "autopep8>=1.4.0",
            "python-editor>=1.0.4",
            "setuptools>=40.0.0",
            "wheel>=0.32.0"
        ),
        entry_points = {
            "console_scripts" : (
                PKG_PREFIX + "config=framework.cli:config",
                PKG_PREFIX + "init=framework.cli:init",
                PKG_PREFIX + "update=framework.cli:update",
                PKG_PREFIX + "pre-commit=framework.hooks:pre_commit",
                PKG_PREFIX + "prepare-commit-msg=framework.hooks:"
                    "prepare_commit_msg",)
        },
        package_data = {
            "framework": [os.path.join("data", file_) for file_ in (
                "LICENSE", "COPYING.LESSER", "MANIFEST.in", ".gitignore",
                ".travis.yml")]
        }
    )


if __name__ == "__main__":
    main()
