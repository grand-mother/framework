# -*- coding: utf-8 -*-
"""
Unit tests for the framework.init module
"""

import os
import sys
import unittest
from cStringIO import StringIO

import setup


class CallContext(object):
    """context for encapsulating an executable call"""
    def __init__(self, *args):
        self._args = args
        self.stdout = StringIO()
        self.stderr = StringIO()

    def __enter__(self):
        self._backup = (sys.argv, sys.stdout, sys.stderr)
        sys.argv = self._args
        sys.stdout = self.stdout
        sys.stderr = self.stderr
        return self

    def __exit__(self, typ, value, traceback):
        sys.argv, sys.stdout, sys.stderr = self._backup


class SetupTest(unittest.TestCase):
    """Unit tests for the init module"""

    @classmethod
    def setUpClass(cls):
        cls._pwd = os.getcwd()
        path = os.path.dirname(__file__)
        path = os.path.join(path, "..")
        os.chdir(path)

    @classmethod
    def tearDownClass(cls):
        os.chdir(cls._pwd)

    def run_setup(*args):
        with CallContext("setup.py", *args) as context:
            setup.main()
        self.assertEqual(context.stderr.getvalue(), "")

    def test_build(self):
        with CallContext("setup.py", "build") as context:
            setup.main()
        self.assertEqual(context.stderr.getvalue(), "")

    def test_dist(self):
        with CallContext("setup.py", "sdist", "bdist_wheel") as context:
            setup.main()
        self.assertEqual(context.stderr.getvalue(), "")
 
    def test_distclean(self):
        with CallContext("setup.py", "distclean") as context:
            setup.main()
        self.assertEqual(context.stderr.getvalue(), "")


if __name__ == "__main__":
    unittest.main()
