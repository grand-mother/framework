# -*- coding: utf-8 -*-
"""
Base unit tests for the framework package
"""

import unittest
import subprocess
import sys

import framework


def system(cmd):
    """system call without error check"""
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
    out, _ = p.communicate()
    return out


class VersionTest(unittest.TestCase):
    """Unit tests for the version module"""

    def test_hash(self):
        githash = system("git rev-parse HEAD").strip()
        self.assertEqual(githash, framework.version.__githash__)

    def test_version(self):
        self.assertIsNotNone(framework.version.__version__)


if __name__ == "__main__":
    unittest.main()
