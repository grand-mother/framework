# -*- coding: utf-8 -*-

from framework.setup import setup_package


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
        entry_points = {
            "console_scripts" : (
                "gfw-init=framework.init:main",
                "gfw-pre-commit=framework.hooks:pre_commit",)
        },
        data_files = [("data", [
            "LICENSE", "COPYING.LESSER", "MANIFEST.in", ".gitignore",
            ".travis.yml"])]
    )
