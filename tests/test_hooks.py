# -*- coding: utf-8 -*-
"""
Unit tests for the framework.hooks module
"""

import os
import shutil
import unittest

from framework import hooks


class HooksTest(unittest.TestCase):
    """Unit tests for the init module"""

    @classmethod
    def setUpClass(cls):
        cls._pwd = os.getcwd()
        path = os.path.dirname(__file__)
        path = os.path.join(path, "..")
        os.chdir(path)

        cls._tmpdir = "tmp"
        os.mkdir(cls._tmpdir)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls._tmpdir)
        os.chdir(cls._pwd)

    def test_pre_commit(self):
        with self.assertRaises(SystemExit) as context:
            hooks.pre_commit()
        self.assertEqual(context.exception.code, 0)

    def test_prepare_commit_msg(self):
        file_ = "tmp/COMMIT_MSG"
        with open(file_, "w") as f:
            msg = os.linesep.join((
                "Initial commit",
                ""
                "# This is a test of course",
                ""))
            f.write(msg)

        with self.assertRaises(SystemExit) as context:
            hooks.prepare_commit_msg(file_)
        self.assertEqual(context.exception.code, 0)


if __name__ == "__main__":
    unittest.main()
