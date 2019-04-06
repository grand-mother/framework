# -*- coding: utf-8 -*-
"""
Run all unit tests for the grand_tools package
"""
import os
import unittest
import sys

try:
    from . import additional_tests
except ImportError:
    # This is a hack for a bug in `coverage` that does not support relative
    # imports from the __main__
    path = os.path.abspath(os.path.dirname(__file__))
    sys.path.append(path)
    from tests import additional_tests


def suite():
    # Load the unit tests
    test_loader = unittest.TestLoader()
    path = os.path.dirname(__file__)
    suite = test_loader.discover(path, pattern="test_*.py")

    for test in additional_tests():
        suite.addTest(test)

    return suite


if __name__ == "__main__":
    runner = unittest.TextTestRunner(verbosity=2)
    r = not runner.run(suite()).wasSuccessful()
    sys.exit(r)
