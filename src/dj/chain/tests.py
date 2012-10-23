#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2012 by Łukasz Langa
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

"""Tests for chain."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals


from django.test import TestCase


class SimpleTest(TestCase):
    def test_dummy(self):
        """Just see if the import works as expected."""
        from dj import chain

    def test_chain_simple(self, c=None):
        from dj.chain import chain 
        if not c:
            c = chain((1,2), [3,4], "56")
            c.xform = lambda v: int(v)
            c.xfilter = lambda v: int(v) % 2 == 0
        self.assertEqual((2,4,6), tuple(c))
        self.assertEqual(3, len(c))
        self.assertEqual((4,6), tuple(c[1:]))
        self.assertEqual(2, len(c[1:]))
        self.assertEqual((4,6), tuple(c[1:3]))
        self.assertEqual(2, len(c[1:3]))
        self.assertEqual((2,4), tuple(c[:2]))
        self.assertEqual(2, len(c[:2]))
        self.assertEqual((2,), tuple(c[:2:2]))
        self.assertEqual(1, len(c[:2:2]))
        self.assertEqual((2,6), tuple(c[::2]))
        self.assertEqual(2, len(c[::2]))
        self.assertEqual(6, c[2])

        try:
            c[3]
            self.fail("Index error not raised.")
        except IndexError:
            pass
        c.xfilter = lambda v: True
        self.assertEqual((1,2,3,4,5,6), tuple(c))
        self.assertEqual(6, len(c))
        self.assertEqual((5,6), tuple(c[4:]))
        self.assertEqual(2, len(c[4:]))
        self.assertEqual((3,4), tuple(c[2:4]))
        self.assertEqual(2, len(c[2:4]))
        self.assertEqual((1,2,3,4), tuple(c[:4]))
        self.assertEqual(4, len(c[:4]))
        self.assertEqual((1,3), tuple(c[:4:2]))
        self.assertEqual(2, len(c[:4:2]))
        self.assertEqual((1,4), tuple(c[::3]))
        self.assertEqual(2, len(c[::3]))
        self.assertEqual(6, c[5])
        try:
            c[6]
            self.fail("Index error not raised.")
        except IndexError:
            pass
        try:
            c[-1]
            self.fail("Value error not raised.")
        except ValueError:
            pass
        try:
            c["boo"]
            self.fail("Value error not raised.")
        except ValueError:
            pass

    def test_chain_simple_copy(self):
        from dj.chain import chain
        c = chain((1,2), [3,4], "56")
        c.xform = lambda v: int(v)
        c.xfilter = lambda v: int(v) % 2 == 0
        c2 = c.copy(*c.iterables)
        self.test_chain_simple(c2)

    def test_chain_sorted(self, c=None):
        from dj.chain import chain
        if not c:
            c = chain((1,2), [3,4], "56")
            c.xform = lambda v: int(v)
            c.xkey = lambda v: -int(v)
            c.xfilter = lambda v: int(v) % 2 == 0
        self.assertEqual((6,4,2), tuple(c))
        self.assertEqual(3, len(c))
        self.assertEqual((4,2), tuple(c[1:]))
        self.assertEqual(2, len(c[1:]))
        self.assertEqual((4,2), tuple(c[1:3]))
        self.assertEqual(2, len(c[1:3]))
        self.assertEqual((6,4), tuple(c[:2]))
        self.assertEqual(2, len(c[:2]))
        self.assertEqual((6,), tuple(c[:2:2]))
        self.assertEqual(1, len(c[:2:2]))
        self.assertEqual((6,2), tuple(c[::2]))
        self.assertEqual(2, len(c[::2]))
        self.assertEqual(2, c[2])
        try:
            c[3]
            self.fail("Index error not raised.")
        except IndexError:
            pass
        c.xfilter = lambda v: True
        self.assertEqual((5,6,3,4,1,2), tuple(c))
        self.assertEqual(6, len(c))
        self.assertEqual((1,2), tuple(c[4:]))
        self.assertEqual(2, len(c[4:]))
        self.assertEqual((3,4), tuple(c[2:4]))
        self.assertEqual(2, len(c[2:4]))
        self.assertEqual((5,6,3,4), tuple(c[:4]))
        self.assertEqual(4, len(c[:4]))
        self.assertEqual((5,3), tuple(c[:4:2]))
        self.assertEqual(2, len(c[:4:2]))
        self.assertEqual((5,4), tuple(c[::3]))
        self.assertEqual(2, len(c[::3]))
        self.assertEqual(2, c[5])
        try:
            c[6]
            self.fail("Index error not raised.")
        except IndexError:
            pass
        try:
            c[-1]
            self.fail("Value error not raised.")
        except ValueError:
            pass
        try:
            c["boo"]
            self.fail("Value error not raised.")
        except ValueError:
            pass

    def test_chain_sorted_copy(self):
        from dj.chain import chain
        c = chain((1,2), [3,4], "56")
        c.xform = lambda v: int(v)
        c.xkey = lambda v: -int(v)
        c.xfilter = lambda v: int(v) % 2 == 0
        c2 = c.copy(*c.iterables)
        self.test_chain_sorted(c2)

    def test_chain_sorted_django_factory(self):
        from dj.chain import chain
        c = chain(("8",1,2,"8"), [8,3,4,8], "8568")
        c.xform = lambda v: int(v)
        c.xkey = lambda v: -int(v)
        c.xfilter = lambda v: int(v) % 2 == 0
        c2 = c._django_factory("__getslice__", 1, 3)
        self.test_chain_sorted(c2)
