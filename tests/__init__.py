# -*- coding: utf-8 -*-
"""
Unit tests for the grand_tools package
"""

import doctest
import os
import unittest

__all__ = ["additional_test"]


def additional_tests():
    """Tests for the doc examples"""
    suite = unittest.TestSuite()
    dirname = os.path.join(os.path.dirname(__file__), "..")
    for root, _, filenames in os.walk(os.path.join(dirname, "grand_pkg")):
        for filename in filenames:
            if filename == '__init__.py' or filename[-3:] != '.py':
                continue
            module = os.path.join(os.path.relpath(root, dirname), filename)
            module = module.replace('/', '.')
            module = module[:-3]
            suite.addTest(doctest.DocTestSuite(module))
    return suite
