========
dj.chain
========

This module provides a way to chain multiple finite iterables for consumption as
a queryset-compatible object.


Quickstart
----------

Let's start with an example. Say we have a couple of abstract database models
which enables us to reuse fields later on::

  class Titled(db.Model):
      title = db.CharField(max_length=100)

      class Meta:
          abstract = True

  class Dynamic(db.Model):
      duration = db.PositiveIntegerField()

      class Meta:
          abstract = True

We also have concrete database models that share some of those fields::

  class Video(Titled, Dynamic):
      RESOLUTION = (
              (1, '240p'), (2, '320p'), (3, '480p'),
              (4, '720p'), (5, '1080p')
      )

      author = db.CharField(max_length=100)
      resolution = db.IntegerField(choices=RESOLUTION)

  class Song(Titled, Dynamic):
      GENRE = (
              (1, 'Country'), (2, 'Folk'), (3, 'Polka'),
              (4, 'Western'), (5, 'World')
      )

      artist = db.CharField(max_length=100)
      genre = db.IntegerField(choices=GENRE)

Our database already contains some data::

  >>> Video.objects.all()
  [<Video: Psy - Gangnam Style (253 s at 1080p)>,
   <Video: Justin Bieber - Baby (225 s at 720p)>,
   <Video: Lady Gaga - Bad Romance (308 s at 320p)>,
   <Video: Shakira - Waka Waka (211 s at 480p)>]
  >>> Song.objects.all()
  [<Song: Gotye feat. Kimbra - Somebody That I Used to Know (244 s; Folk)>,
   <Song: Coldplay - Clocks (307 s; Polka)>,
   <Song: Muse - Madness (279 s; Country)>,
   <Song: Florence + The Machine - Spectrum (218 s; Folk)>]


A basic chain
~~~~~~~~~~~~~

Let's create a simple chain::

  >>> from dj.chain import chain
  >>> media = chain(Video.objects.all(), Song.objects.all())

We can collectively call queryset-related methods on it::

  >>> media.count()
  8

We can also filter it further::

  >>> list(media.filter(duration__gt=250))
  [<Video: Psy - Gangnam Style (253 s at 1080p)>,
   <Video: Lady Gaga - Bad Romance (308 s at 320p)>,
   <Song: Coldplay - Clocks (307 s; Polka)>,
   <Song: Muse - Madness (279 s; Country)>]

Check the cumulative length::

  >>> media.filter(duration__gt=250).count()
  4

Use indices and slices::

  >>> media.filter(duration__gt=250)[1]
  <Video: Lady Gaga - Bad Romance (308 s at 320p)>
  >>> list(media[3:6])
  [<Video: Shakira - Waka Waka (211 s at 480p)>,
   <Song: Gotye feat. Kimbra - Somebody That I Used to Know (244 s; Folk)>,
   <Song: Coldplay - Clocks (307 s; Polka)>]
  >>> list(media[1::3])
  [<Video: Justin Bieber - Baby (225 s at 720p)>, 
   <Song: Gotye feat. Kimbra - Somebody That I Used to Know (244 s; Folk)>,
   <Song: Florence + The Machine - Spectrum (218 s; Folk)>]

Use cumulative sorting and filtering::

  >>> list(media.order_by('title'))
  [<Video: Justin Bieber - Baby (225 s at 720p)>,
   <Video: Lady Gaga - Bad Romance (308 s at 320p)>,
   <Song: Coldplay - Clocks (307 s; Polka)>,
   <Video: Psy - Gangnam Style (253 s at 1080p)>,
   <Song: Muse - Madness (279 s; Country)>,
   <Song: Gotye feat. Kimbra - Somebody That I Used to Know (244 s; Folk)>,
   <Song: Florence + The Machine - Spectrum (218 s; Folk)>,
   <Video: Shakira - Waka Waka (211 s at 480p)>]
  >>> list(media.order_by('-duration').filter(duration__lt=300))
  [<Song: Muse - Madness (279 s; Country)>,
   <Video: Psy - Gangnam Style (253 s at 1080p)>,
   <Song: Gotye feat. Kimbra - Somebody That I Used to Know (244 s; Folk)>,
   <Video: Justin Bieber - Baby (225 s at 720p)>,
   <Song: Florence + The Machine - Spectrum (218 s; Folk)>,
   <Video: Shakira - Waka Waka (211 s at 480p)>]

Etc.


Chaining heterogenic iterables
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

We can add iterables that aren't querysets to the bunch::

  >>> from collections import namedtuple
  >>> Book = namedtuple('Book', "author title page_count")
  >>> books=(
  ... Book(author='Charles Dickens', title='A Tale of Two Cities', page_count=869),
  ... Book(author='Miguel de Cervantes', title='Don Quixote', page_count=1212),
  ... )
  >>> media=chain(Video.objects.all(), books)
  >>> media.count()
  6
  >>> list(media)
  [<Video: Psy - Gangnam Style (253 s at 1080p)>,
   <Video: Justin Bieber - Baby (225 s at 720p)>,
   <Video: Lady Gaga - Bad Romance (308 s at 320p)>,
   <Video: Shakira - Waka Waka (211 s at 480p)>,
   Book(author='Charles Dickens', title='A Tale of Two Cities', page_count=869),
   Book(author='Miguel de Cervantes', title='Don Quixote', page_count=1212)]

You can also use cumulative ordering in this case. The only thing you need to
keep in mind is that iterables which are not querysets should be presorted for
the cumulative result to be ordered correctly. An example::

  >>> list(media.order_by('title'))
  [Book(author='Charles Dickens', title='A Tale of Two Cities', page_count=869),
   <Video: Justin Bieber - Baby (225 s at 720p)>,
   <Video: Lady Gaga - Bad Romance (308 s at 320p)>,
   Book(author='Miguel de Cervantes', title='Don Quixote', page_count=1212),
   <Video: Psy - Gangnam Style (253 s at 1080p)>,
   <Video: Shakira - Waka Waka (211 s at 480p)>]


Custom filtering, sorting and transformations
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Chains provide special overridable static methods used while yielding values:

* ``xfilter(value)`` - yield a value only if ``xfilter(value)`` returns
  ``True``. See known issues below.

* ``xform(value)`` - transforms the value JIT before yielding it back. It is
  only called for values within the specified slice and those which passed
  ``xfilter``.

* ``xkey(value)`` - returns a value to be used in comparison between elements if
  sorting should be used. Individual iterables should be presorted for the
  complete result to be sorted properly. Any cumulative ``order_by`` clauses are
  executed before the ``xkey`` method is used. 


Known issues
------------

1. If slicing or ``xfilter`` is used, reported ``len()`` is computed by
   iterating over all iterables so performance is weak. Note that ``len()`` is
   used by ``list()`` when you convert your chain to a list or when iterating
   over the chain in Django templates.  If this is not expected, you can convert
   to a list using a workaround like this::

       list(e for e in some_chain)

2. Indexing on chains uses iteration underneath so performance is weak. This
   feature is only available as a last resort. Slicing on the other hand is also
   lazy.

3. Collective ``filter`` and ``exclude`` silently skip filtering on incompatible
   iterables. Use ``xfilter(value)`` as a workaround.


How do I run the tests?
-----------------------

The easiest way would be to run::

  $ DJANGO_SETTINGS_MODULE="dj._chaintestproject.settings" django-admin.py test


Change Log
----------

0.9.0
~~~~~

* code separated from ``lck.django``

* support for collective sort using queryset-like ``order_by`` on a chain

* fix for slices with custom steps

* PEP8-fied all sources 


Authors
-------

Glued together by `Łukasz Langa <mailto:lukasz@langa.pl>`_.
