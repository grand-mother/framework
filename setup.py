# -*- coding: utf-8 -*-

from framework import setup_package


# The package version
MAJOR = 0
MINOR = 0
MICRO = 0


# Extra package meta data can be added here. For a full list of available
# classifiers, see:
#     https://pypi.org/pypi?%3Aaction=list_classifiers
EXTRA_CLASSIFIERS = (
    "Development Status :: 3 - Alpha",
)


if __name__ == "__main__":
    setup_package(
        # Framework arguments
        __file__, (MAJOR, MINOR, MICRO), EXTRA_CLASSIFIERS,

        # Vanilla setuptools.setup arguments
        install_requires = (
            "setuptools>=40.0.0",
            "wheel>=0.32.0"
        ),
        entry_points = {
            "console_scripts" : (
                "grand-pkg-init=framework.init:main",
                "grand-pre-commit=framework.hooks:pre_commit",)
        },
        data_files = [(".", [
            "LICENSE", "COPYING.LESSER", "MANIFEST.in", ".gitignore",
            ".travis.yml"])]
    )
