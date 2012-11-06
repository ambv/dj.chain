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
        from dj import chain  # noqa

    def test_chain_simple(self, c=None):
        from dj.chain import chain
        if not c:
            c = chain((1, 2), [3, 4], "56")
            c.xform = lambda v: int(v)
            c.xfilter = lambda v: int(v) % 2 == 0
        self.assertEqual((2, 4, 6), tuple(c))
        self.assertEqual(3, len(c))
        self.assertEqual((4, 6), tuple(c[1:]))
        self.assertEqual(2, len(c[1:]))
        self.assertEqual((4, 6), tuple(c[1:3]))
        self.assertEqual(2, len(c[1:3]))
        self.assertEqual((2, 4), tuple(c[:2]))
        self.assertEqual(2, len(c[:2]))
        self.assertEqual((2,), tuple(c[:2:2]))
        self.assertEqual(1, len(c[:2:2]))
        self.assertEqual((2, 6), tuple(c[::2]))
        self.assertEqual(2, len(c[::2]))
        self.assertEqual(6, c[2])

        try:
            c[3]
            self.fail("Index error not raised.")
        except IndexError:
            pass
        c.xfilter = lambda v: True
        self.assertEqual((1, 2, 3, 4, 5, 6), tuple(c))
        self.assertEqual(6, len(c))
        self.assertEqual((5, 6), tuple(c[4:]))
        self.assertEqual(2, len(c[4:]))
        self.assertEqual((3, 4), tuple(c[2:4]))
        self.assertEqual(2, len(c[2:4]))
        self.assertEqual((1, 2, 3, 4), tuple(c[:4]))
        self.assertEqual(4, len(c[:4]))
        self.assertEqual((1, 3), tuple(c[:4:2]))
        self.assertEqual(2, len(c[:4:2]))
        self.assertEqual((1, 4), tuple(c[::3]))
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
        c = chain((1, 2), [3, 4], "56")
        c.xform = lambda v: int(v)
        c.xfilter = lambda v: int(v) % 2 == 0
        c2 = c.copy(*c.iterables)
        self.test_chain_simple(c2)

    def test_chain_sorted(self, c=None):
        from dj.chain import chain
        if not c:
            c = chain((1, 2), [3, 4], "56")
            c.xform = lambda v: int(v)
            c.xkey = lambda v: -int(v)
            c.xfilter = lambda v: int(v) % 2 == 0
        self.assertEqual((6, 4, 2), tuple(c))
        self.assertEqual(3, len(c))
        self.assertEqual((4, 2), tuple(c[1:]))
        self.assertEqual(2, len(c[1:]))
        self.assertEqual((4, 2), tuple(c[1:3]))
        self.assertEqual(2, len(c[1:3]))
        self.assertEqual((6, 4), tuple(c[:2]))
        self.assertEqual(2, len(c[:2]))
        self.assertEqual((6,), tuple(c[:2:2]))
        self.assertEqual(1, len(c[:2:2]))
        self.assertEqual((6, 2), tuple(c[::2]))
        self.assertEqual(2, len(c[::2]))
        self.assertEqual(2, c[2])
        try:
            c[3]
            self.fail("Index error not raised.")
        except IndexError:
            pass
        c.xfilter = lambda v: True
        self.assertEqual((5, 6, 3, 4, 1, 2), tuple(c))
        self.assertEqual(6, len(c))
        self.assertEqual((1, 2), tuple(c[4:]))
        self.assertEqual(2, len(c[4:]))
        self.assertEqual((3, 4), tuple(c[2:4]))
        self.assertEqual(2, len(c[2:4]))
        self.assertEqual((5, 6, 3, 4), tuple(c[:4]))
        self.assertEqual(4, len(c[:4]))
        self.assertEqual((5, 3), tuple(c[:4:2]))
        self.assertEqual(2, len(c[:4:2]))
        self.assertEqual((5, 4), tuple(c[::3]))
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
        c = chain((1, 2), [3, 4], "56")
        c.xform = lambda v: int(v)
        c.xkey = lambda v: -int(v)
        c.xfilter = lambda v: int(v) % 2 == 0
        c2 = c.copy(*c.iterables)
        self.test_chain_sorted(c2)

    def test_chain_sorted_django_factory(self):
        from dj.chain import chain
        c = chain(("8", 1, 2, "8"), [8, 3, 4, 8], "8568")
        c.xform = lambda v: int(v)
        c.xkey = lambda v: -int(v)
        c.xfilter = lambda v: int(v) % 2 == 0
        c2 = c._django_factory("__getslice__", 1, 3)
        self.test_chain_sorted(c2)


class MediaTest(TestCase):
    def setUp(self):
        from dj._chaintestproject.app.models import Video, Song
        v1 = Video(
            author='Psy', title='Gangnam Style', duration=253, resolution=5,
        )
        v1.save()
        v2 = Video(
            author='Justin Bieber', title='Baby', duration=225, resolution=4,
        )
        v2.save()
        v3 = Video(
            author='Lady Gaga', title='Bad Romance', duration=308,
            resolution=2
        )
        v3.save()
        v4 = Video(
            author='Shakira', title='Waka Waka', duration=211, resolution=3,
        )
        v4.save()
        s1 = Song(
            artist='Gotye feat. Kimbra', title='Somebody That I Used to Know',
            duration=244, genre=2,
        )
        s1.save()
        s2 = Song(
            artist='Coldplay', title='Clocks', duration=307, genre=3,
        )
        s2.save()
        s3 = Song(
            artist='Muse', title='Madness', duration=279, genre=1,
        )
        s3.save()
        s4 = Song(
            artist='Florence + The Machine', title='Spectrum', duration=218,
            genre=2,
        )
        s4.save()
        from collections import namedtuple
        Book = namedtuple('Book', "author title page_count")
        self.books = (
            Book(
                author='Charles Dickens', title='A Tale of Two Cities',
                page_count=869,
            ),
            Book(
                author='Miguel de Cervantes', title='Don Quixote',
                page_count=1212
            ),
        )
        self.Video = Video
        self.Song = Song
        self.Book = Book

    def test_model_consistency(self):
        self.assertEqual(self.Video.objects.count(), 4)
        self.assertEqual(self.Song.objects.count(), 4)
        self.assertEqual(len(self.books), 2)

    def test_basic_chain(self):
        from dj.chain import chain
        media = chain(self.Video.objects.all(), self.Song.objects.all())
        self.assertEqual(media.count(), 8)
        self.assertEqual(
            list(media.filter(duration__gt=250)),
            list(self.Video.objects.filter(title__in=('Gangnam Style',
                 'Bad Romance')).order_by('-title')) +
            list(self.Song.objects.filter(title__in=('Clocks',
                 'Madness')).order_by('title'))
        )
        self.assertEqual(media.filter(duration__gt=250).count(), 4)
        self.assertEqual(
            media.filter(duration__gt=250)[1],
            self.Video.objects.get(title='Bad Romance')
        )
        self.assertEqual(
            list(media[3:6]),
            [self.Video.objects.get(title='Waka Waka')] +
            list(self.Song.objects.filter(artist__in=('Gotye feat. Kimbra',
                 'Coldplay')).order_by('-artist'))
        )
        self.assertEqual(list(media[1::3]), [
            self.Video.objects.get(title='Baby'),
            self.Song.objects.get(artist='Gotye feat. Kimbra'),
            self.Song.objects.get(title='Spectrum'),
        ])
        self.assertEqual(list(media[:5:4]), [
            self.Video.objects.get(title='Gangnam Style'),
            self.Song.objects.get(artist='Gotye feat. Kimbra'),
        ])

    def test_collective_sort(self):
        from dj.chain import chain
        media = chain(self.Video.objects.all(), self.Song.objects.all())
        dur_asc = media.order_by('duration')
        self.assertEqual(dur_asc[0].duration, 211)
        self.assertEqual(dur_asc[1].duration, 218)
        self.assertEqual(dur_asc[2].duration, 225)
        self.assertEqual(dur_asc[3].duration, 244)
        self.assertEqual(dur_asc[4].duration, 253)
        self.assertEqual(dur_asc[5].duration, 279)
        self.assertEqual(dur_asc[6].duration, 307)
        self.assertEqual(dur_asc[7].duration, 308)
        dur_desc = media.order_by('-duration')
        self.assertEqual(dur_desc[7].duration, 211)
        self.assertEqual(dur_desc[6].duration, 218)
        self.assertEqual(dur_desc[5].duration, 225)
        self.assertEqual(dur_desc[4].duration, 244)
        self.assertEqual(dur_desc[3].duration, 253)
        self.assertEqual(dur_desc[2].duration, 279)
        self.assertEqual(dur_desc[1].duration, 307)
        self.assertEqual(dur_desc[0].duration, 308)
        title_asc = media.order_by('title')
        self.assertEqual(title_asc[0].title, 'Baby')
        self.assertEqual(title_asc[1].title, 'Bad Romance')
        self.assertEqual(title_asc[2].title, 'Clocks')
        self.assertEqual(title_asc[3].title, 'Gangnam Style')
        self.assertEqual(title_asc[4].title, 'Madness')
        self.assertEqual(title_asc[5].title, 'Somebody That I Used to Know')
        self.assertEqual(title_asc[6].title, 'Spectrum')
        self.assertEqual(title_asc[7].title, 'Waka Waka')
        title_desc = media.order_by('-title')
        self.assertEqual(title_desc[7].title, 'Baby')
        self.assertEqual(title_desc[6].title, 'Bad Romance')
        self.assertEqual(title_desc[5].title, 'Clocks')
        self.assertEqual(title_desc[4].title, 'Gangnam Style')
        self.assertEqual(title_desc[3].title, 'Madness')
        self.assertEqual(title_desc[2].title, 'Somebody That I Used to Know')
        self.assertEqual(title_desc[1].title, 'Spectrum')
        self.assertEqual(title_desc[0].title, 'Waka Waka')

    def test_heterogenic_sort(self):
        from dj.chain import chain
        media = chain(self.Video.objects.all(), self.books)
        title_asc = media.order_by('title')
        self.assertEqual(title_asc[0].title, 'A Tale of Two Cities')
        self.assertEqual(title_asc[1].title, 'Baby')
        self.assertEqual(title_asc[2].title, 'Bad Romance')
        self.assertEqual(title_asc[3].title, 'Don Quixote')
        self.assertEqual(title_asc[4].title, 'Gangnam Style')
        self.assertEqual(title_asc[5].title, 'Waka Waka')
        # No descending test since it would have rendered incorrect results
        # anyway: non-queryset iterables have to be presorted for the result
        # to be correctly ordered.
