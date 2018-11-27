# -*- coding: utf-8 -*-
"""
Unit tests for the framework.version module
"""

import unittest
import sys

import framework
from framework import git


class VersionTest(unittest.TestCase):
    """Unit tests for the version module"""

    def test_hash(self):
        githash, _ = git("rev-parse", "HEAD")
        self.assertEqual(githash.strip(), framework.version.__githash__)

    def test_version(self):
        self.assertIsNotNone(framework.version.__version__)


if __name__ == "__main__":
    unittest.main()
