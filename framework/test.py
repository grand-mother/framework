# -*- coding: utf-8 -*-
"""
Encapsulation of setuptools for GRAND

Copyright (C) 2018 The GRAND collaboration

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>
"""

import sys

from cStringIO import StringIO

__all__ = [ "RunContext" ]


class RunContext(object):
    """Context for encapsulating an executable call"""
    def __init__(self, *args):
        self._args = list(args)
        self._stdout = StringIO()
        self._stderr = StringIO()
        self.out = None
        self.err = None
        self.code = None

    def __enter__(self):
        self._backup = (sys.argv, sys.stdout, sys.stderr)
        sys.argv = self._args
        sys.stdout = self._stdout
        sys.stderr = self._stderr
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        sys.argv, sys.stdout, sys.stderr = self._backup
        self.out = self._stdout.getvalue()
        self.err = self._stderr.getvalue()
        if exc_type == SystemExit:
            self.code = exc_value.code
            return True
        return False
