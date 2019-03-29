# -*- coding: utf-8 -*-
"""
Unit tests for the framework.init module
"""

import os
import shutil
import sys
import unittest

from framework import cli, RunContext


class InitTest(unittest.TestCase):
    """Unit tests for the init command"""

    @classmethod
    def setUpClass(cls):
        cls._pwd = os.getcwd()
        path = os.path.dirname(__file__)
        path = os.path.join(path, "..")
        os.chdir(path)

        cls.tmpdir = ".git/.tmp"
        os.mkdir(cls.tmpdir)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmpdir)
        os.chdir(cls._pwd)

    def create(self, package_name, code=0):
        path = os.path.join(self.tmpdir, package_name)
        args = ("grand-pkg-init", "--default", "--quiet", path) 
        with RunContext(*args) as context:
            cli.init()
        self.assertEqual(context.err, "")
        self.assertEqual(context.code, code)

    def test_create_simple(self):
        self.create("toto")

    def test_create_composite(self):
        self.create("toto-composite")

    def test_create_nested(self):
        self.create(os.path.join("tata", "toto-composite"))

    def test_existing(self):
        self.create("toto", code=1)

    def test_import(self):
        path = os.path.join(self.tmpdir, "toto")
        sys.path.append(path)
        try:
            import toto
        except Exception as e:
            self.fail(e)
        self.assertEqual(toto.__version__, None)
        self.assertEqual(toto.__githash__, None)


if __name__ == "__main__":
    unittest.main()
