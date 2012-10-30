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

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from django.db import models as db


class Titled(db.Model):
    title = db.CharField(max_length=100)

    class Meta:
        abstract = True


class Dynamic(db.Model):
    duration = db.PositiveIntegerField()

    class Meta:
        abstract = True


class Video(Titled, Dynamic):
    RESOLUTION = (
            (1, '240p'), (2, '320p'), (3, '480p'),
            (4, '720p'), (5, '1080p')
    )

    author = db.CharField(max_length=100)
    resolution = db.IntegerField(choices=RESOLUTION)

    def __unicode__(self):
        return "{} - {} ({} s at {})".format(
                self.author, self.title, self.duration,
                self.get_resolution_display())

class Song(Titled, Dynamic):
    GENRE = (
            (1, 'Country'), (2, 'Folk'), (3, 'Polka'),
            (4, 'Western'), (5, 'World')
    )

    artist = db.CharField(max_length=100)
    genre = db.IntegerField(choices=GENRE)

    def __unicode__(self):
        return "{} - {} ({} s; {})".format(
                self.artist, self.title, self.duration,
                self.get_genre_display())
