# -*- coding: utf-8 -*-
"""
Unit tests for the framework.hooks module
"""

import os
import shutil
import unittest

from framework import hooks, RunContext


class HooksTest(unittest.TestCase):
    """Unit tests for the hook module"""

    @classmethod
    def setUpClass(cls):
        cls._pwd = os.getcwd()
        path = os.path.dirname(__file__)
        path = os.path.join(path, "..")
        os.chdir(path)

        cls._tmpdir = ".git/.tmp"
        os.makedirs(cls._tmpdir)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls._tmpdir)
        os.chdir(cls._pwd)

    def test_pre_commit(self):
        with RunContext("pre-commit") as context:
            hooks.pre_commit()

        # Clean any modified file
        for file_ in (".stats.json", "README.md"):
            hooks.git("reset", file_)
            hooks.git("checkout", file_)

        self.assertEqual(context.code, 0)

    def test_prepare_commit_msg(self):
        file_ = os.path.join(self._tmpdir, "COMMIT_MSG")
        with open(file_, "w") as f:
            msg = os.linesep.join((
                "Initial commit",
                ""
                "# This is a test of course",
                ""))
            f.write(msg)

        with RunContext("prepare-commit-msg", file_) as context:
            hooks.prepare_commit_msg()
        self.assertEqual(context.code, 0)


if __name__ == "__main__":
    unittest.main()
