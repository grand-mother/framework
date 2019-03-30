# -*- coding: utf-8 -*-
"""
Unit tests for the framework.init module
"""

import json
import os
import shutil
import sys
import unittest

from framework import cli, RunContext


class CLITest(unittest.TestCase):
    """Unit tests for the CLI"""

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

    def tearDown(self):
        os.chdir(self._pwd)

    def cd_tmp(self, path):
        path = os.path.join(self.tmpdir, path)
        os.chdir(path)

    def cd_head(self):
        os.chdir(self._pwd)

    def config(self, *args):
        args = ("grand-pkg-config", *args)
        with RunContext(*args) as context:
            cli.config()
        return context

    def init(self, package_name, code=0):
        path = os.path.join(self.tmpdir, package_name)
        args = ("grand-pkg-init", "--default", "--quiet", path) 
        with RunContext(*args) as context:
            cli.init()
        self.assertEqual(context.err, "")
        self.assertEqual(context.code, code)

    def update(self, package_name, code=0):
        path = os.path.join(self.tmpdir, package_name)
        args = ("grand-pkg-update", "--quiet", path)
        with RunContext(*args) as context:
            cli.update()
        self.assertEqual(context.err, "")
        self.assertEqual(context.code, code)

    def test_create_simple(self):
        path = "toto"
        self.init(path)
        self.update(path)

    def test_create_composite(self):
        path = "toto-composite"
        self.init(path)
        self.update(path)

    def test_create_nested(self):
        self.init(os.path.join("tata", "toto-composite"))

    def test_upper(self):
        self.init("Tutu", code=0)

    def test_existing(self):
        self.init("toto", code=1)

    def test_config(self):
        name = "titi"
        description = "Add a brief description"
        self.init(name)
        self.cd_tmp(name)

        # Test the named setters & getters
        r = self.config("name")
        self.assertEqual(r.code, 0)
        self.assertEqual(r.out.strip(), name)
        r = self.config("name", "toto")
        self.assertEqual(r.code, 0)
        r = self.config("name")
        self.assertEqual(r.code, 0)
        self.assertEqual(r.out.strip(), "toto")
        r = self.config("name", name)
        self.assertEqual(r.code, 0)

        r = self.config("git-name")
        self.assertEqual(r.code, 0)
        self.assertEqual(r.out.strip(), name)
        r = self.config("git-name", "toto")
        self.assertEqual(r.code, 0)
        r = self.config("git-name")
        self.assertEqual(r.code, 0)
        self.assertEqual(r.out.strip(), "toto")
        r = self.config("git-name", name)
        self.assertEqual(r.code, 0)

        r = self.config("dist-name")
        self.assertEqual(r.code, 0)
        self.assertEqual(r.out.strip(), "grand-"+name)
        r = self.config("dist-name", "toto")
        self.assertEqual(r.code, 0)
        r = self.config("dist-name")
        self.assertEqual(r.code, 0)
        self.assertEqual(r.out.strip(), "toto")
        r = self.config("dist-name", "grand-" + name)
        self.assertEqual(r.code, 0)

        r = self.config("description")
        self.assertEqual(r.code, 0)
        self.assertEqual(r.out.strip(), description)
        r = self.config("description", "toto")
        self.assertEqual(r.code, 0)
        r = self.config("description")
        self.assertEqual(r.code, 0)
        self.assertEqual(r.out.strip(), "toto")
        r = self.config("description", description)
        self.assertEqual(r.code, 0)

        # Test the config dump
        r = self.config("")
        self.assertEqual(r.code, 0)
        r = json.loads(r.out)
        self.assertEqual(r.pop("name"), name)
        self.assertEqual(r.pop("git-name"), name)
        self.assertEqual(r.pop("dist-name"), "grand-" + name)
        self.assertEqual(r.pop("description"), description)
        self.assertEqual(len(r), 0)

        # Test the out of package case
        os.chdir("/tmp")
        r = self.config("")
        self.assertEqual(r.code, 1)
        self.assertEqual(r.err.strip(), "Not a GRAND package ...")
        self.cd_head()
        self.cd_tmp(name)

        # Test the invalid parameter case
        r = self.config("toto")
        self.assertEqual(r.code, 1)
        self.assertEqual(r.err.strip(), "Invalid parameter `toto' ...")

        r = self.config("toto", "titi")
        self.assertEqual(r.code, 1)
        self.assertEqual(r.err.strip(), "Invalid parameter `toto' ...")

        # Test the bad name cases
        r = self.config("name", "Toto")
        self.assertEqual(r.code, 1)
        self.assertEqual(r.err.strip(), "Invalid package name: `Toto' ...")

        r = self.config("name", "1toto")
        self.assertEqual(r.code, 1)
        self.assertEqual(r.err.strip(), "Invalid package name: `1toto' ...")

        r = self.config("name", "grand-toto")
        self.assertEqual(r.code, 1)
        self.assertEqual(r.err.strip(),
                         "Invalid package name: `grand-toto' ...")

        r = self.config("git-name", "Toto")
        self.assertEqual(r.code, 1)
        self.assertEqual(r.err.strip(), "Invalid git name: `Toto' ...")

        r = self.config("git-name", "1toto")
        self.assertEqual(r.code, 1)
        self.assertEqual(r.err.strip(), "Invalid git name: `1toto' ...")

        r = self.config("git-name", "grand_toto")
        self.assertEqual(r.code, 1)
        self.assertEqual(r.err.strip(), "Invalid git name: `grand_toto' ...")

        r = self.config("dist-name", "Toto")
        self.assertEqual(r.code, 1)
        self.assertEqual(r.err.strip(), "Invalid dist name: `Toto' ...")

        r = self.config("dist-name", "1toto")
        self.assertEqual(r.code, 1)
        self.assertEqual(r.err.strip(), "Invalid dist name: `1toto' ...")

        r = self.config("dist-name", "grand_toto")
        self.assertEqual(r.code, 1)
        self.assertEqual(r.err.strip(), "Invalid dist name: `grand_toto' ...")

    def test_import(self):
        path = os.path.join(self.tmpdir, "toto")
        sys.path.append(path)
        try:
            import toto
        except Exception as e:
            self.fail(e)
        self.assertEqual(toto.__version__, None)
        self.assertEqual(toto.__git__, {})


if __name__ == "__main__":
    unittest.main()
