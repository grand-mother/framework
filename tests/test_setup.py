# -*- coding: utf-8 -*-
"""
Unit tests for the grand_pkg.setup module
"""

import os
import unittest

import setup

from grand_pkg import RunContext


class SetupTest(unittest.TestCase):
    """Unit tests for the setup module"""

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
        with RunContext("setup.py", *args) as context:
            setup.main()
        self.assertEqual(context.err, "")

    def test_rebuild(self):
        with RunContext("setup.py", "build") as context:
            setup.main()
        self.assertEqual(context.err, "")

    def test_dist(self):
        with RunContext("setup.py", "sdist", "bdist_wheel") as context:
            setup.main()
        self.assertEqual(context.err, "")
 
    def test_distclean(self):
        with RunContext("setup.py", "distclean") as context:
            setup.main()
        self.assertEqual(context.err, "")


if __name__ == "__main__":
    unittest.main()
