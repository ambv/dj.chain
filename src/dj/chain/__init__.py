#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2011 - 2012 by Łukasz Langa
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

"""dj.chain
   --------

    This module provides a way to chain multiple finite iterables for
    consumption as a QuerySet-compatible object."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from django.core.exceptions import FieldError
from null import unset


class chain(object):
    """Enables chaining multiple iterables to serve them lazily as
    a QuerySet-compatible object. Supports collective ``count()``, ``defer``,
    ``exists()``, ``exclude``, ``extra``, ``filter``, ``only``, ``order_by``,
    ``prefetch_related``, ``select_for_update``, ``select_related`` and
    ``using`` methods.

    Provides special overridable static methods used while yielding values:

      * ``xfilter(value)`` - yield a value only if ``xfilter(value)`` returns
                             ``True``. See known issues below.

      * ``xform(value)`` - transforms the value JIT before yielding it back.
                           It is only called for values within the specified
                           slice and those which passed ``xfilter``.

      * ``xkey(value)`` - returns a value to be used in comparison between
                          elements if sorting should be used. Individual
                          iterables should be presorted for the complete result
                          to be sorted properly.

    Known issues:

    1. If slicing or ``xfilter`` is used, reported ``len()`` is computed by
       iterating over all iterables so performance is weak. Note that ``len()``
       is used by ``list()`` when you convert your chain to a list or when
       iterating over the chain in Django templates. If this is not expected,
       you can convert to a list using a workaround like this::

           list(e for e in some_chain)

    2. Indexing on chains uses iteration underneath so performance is weak.
       This feature is only available as a last resort. Slicing on the other
       hand is also lazy."""

    def __init__(self, *iterables, **kwargs):
        self.iterables = iterables
        self.start = None
        self.stop = None
        self.step = None
        self.strict = kwargs.get('strict', False)
        self.xsort = []
        self.xvalues_mode = None
        self.xvalues_fields = ()
        if self.strict:
            self._django_factory = self._strict_django_factory
        else:
            self._django_factory = self._default_django_factory

    @staticmethod
    def xform(value):
        """Transform the ``value`` just-in-time before yielding it back.
        Default implementation simply returns the ``value`` as is."""
        return value

    @staticmethod
    def xfilter(value=unset):
        """xfilter(value) -> bool

        Only yield the ``value`` if this method returns ``True``.
        Skip to the next iterator value otherwise. Default implementation
        always returns ``True``."""
        return True

    @staticmethod
    def xkey(value=unset):
        """xkey(value) -> comparable value

        Return a value used in comparison between elements if sorting
        should be used."""
        return value

    def copy(self, *iterables):
        """Returns a copy of this chain. If `iterables` are provided,
        they are used instead of the ones in the current object."""
        if not iterables:
            iterables = self.iterables
        result = chain(*iterables)
        result.xfilter = self.xfilter
        result.xform = self.xform
        result.xkey = self.xkey
        result.xsort = list(self.xsort)
        result.xvalues_mode = self.xvalues_mode
        result.xvalues_fields = list(self.xvalues_fields)
        result.start = self.start
        result.stop = self.stop
        result.step = self.step
        result.strict = self.strict
        return result

    def _filtered_next(self, iterator):
        """Raises StopIteration just like regular iterator.next()."""
        result = iterator.next()
        while not self.xfilter(result):
            result = iterator.next()
        return result

    def __iter__(self):
        if self.ordered:
            def _gen():
                candidates = {}
                for iterable in self.iterables:
                    iterator = iter(iterable)
                    try:
                        candidates[iterator] = [self._filtered_next(iterator),
                                                iterator]
                    except StopIteration:
                        continue
                while candidates:
                    clist = candidates.values()
                    for rule in self.xsort[::-1]:
                        reverse = rule[0] == '-'
                        if reverse:
                            rule = rule[1:]
                        clist.sort(key=lambda x: getattr(x[0], rule),
                                   reverse=reverse)
                    try:
                        to_yield, iterator = min(clist,
                                                 key=lambda x: self.xkey(x[0]))
                        yield to_yield
                    except ValueError:
                        # sequence empty
                        break
                    try:
                        candidates[iterator] = [self._filtered_next(iterator),
                                                iterator]
                    except StopIteration:
                        del candidates[iterator]
        else:
            def _gen():  # noqa
                for it in self.iterables:
                    for element in it:
                        if not self.xfilter(element):
                            continue
                        yield element
        for index, element in enumerate(_gen()):
            if self.start and index < self.start:
                continue
            if self.step and (index - (self.start or 0)) % self.step:
                continue
            if self.stop and index >= self.stop:
                break
            yield self.xform(self.xvalue(element))

    def xvalue(self, value):
        """For each field listed in ``xvalues_fields`` try to:

            * use an item of the specified name on the object, if exists

            * call a method of the specified name on the object, if exists

            * use an attribute of the specified name on the object, if exists

            * raise an ``AttributeError`` otherwise

        Return the fiels as a dictionary, list of tuples or a flat list
        depending on the ``xvalue_mode``.
        """
        if not self.xvalues_mode:
            return value
        result = self.xvalues_mode()
        if isinstance(result, tuple):
            # flat list
            field = self.xvalues_fields[0]
            try:
                return value[field]
            except TypeError:
                pass
            v = getattr(value, field)
            return v() if callable(v) else v
        if isinstance(result, list):
            # regular list
            for field in self.xvalues_fields:
                try:
                    result.append(value[field])
                    continue
                except TypeError:
                    pass
                v = getattr(value, field)
                result.append(v() if callable(v) else v)
            result = tuple(result)
        else:
            for field in self.xvalues_fields:
                try:
                    result[field] = value[field]
                    continue
                except TypeError:
                    pass
                v = getattr(value, field)
                result[field] = v() if callable(v) else v
        return result

    def __getitem__(self, key):
        if isinstance(key, slice):
            if any((key.start and key.start < 0,
                    key.stop and key.stop < 0,
                    key.step and key.step < 0)):
                raise ValueError("chains do not support negative indexing")
            result = self.copy()
            result.start = key.start
            result.stop = key.stop
            result.step = key.step
        elif isinstance(key, int):
            if key < 0:
                raise ValueError("chains do not support negative indexing")
            self_without_transform = self.copy()
            self_without_transform.xform = lambda x: x
            for index, elem in enumerate(self_without_transform):
                if index == key:
                    return self.xform(elem)
            raise IndexError("chain index out of range")
        else:
            raise ValueError("chain supports only integer indexing and "
                             "slices.")
        return result

    def __len_parts__(self):
        for iterable in self.iterables:
            try:
                yield iterable.count()
            except:
                try:
                    yield len(iterable)
                except TypeError:
                    yield len(list(iterable))

    def __len__(self):
        try:
            if all((self.xfilter(),
                    not self.start,
                    not self.stop,
                    not self.step or self.step == 1)):
                # fast __len__
                sum = 0
                for sub in self.__len_parts__():
                    sum += sub
                return sum
        except TypeError:
            pass
        # slow __len__ if xfilter or slicing was used
        length = 0
        for length, _ in enumerate(self):
            pass
        return length + 1

    def _default_django_factory(self, _method, *args, **kwargs):
        """Used if strict=False while constructing the chain."""
        new_iterables = []
        for it in self.iterables:
            try:
                new_iterables.append(getattr(it, _method)(*args, **kwargs))
            except (AttributeError, ValueError, TypeError, FieldError):
                new_iterables.append(it)
        return self.copy(*new_iterables)

    def _strict_django_factory(self, _method, *args, **kwargs):
        """Used if strict=True while constructing the chain."""
        # imported here to avoid settings.py bootstrapping issues
        from django.db.models.query import QuerySet
        new_iterables = []
        for it in self.iterables:
            if isinstance(it, QuerySet):
                new_iterables.append(getattr(it, _method)(*args, **kwargs))
            else:
                new_iterables.append(it)
        return self.copy(*new_iterables)

    def all(self):
        return self

    def count(self):
        """QuerySet-compatible ``count`` method. Supports multiple iterables.
        """
        return len(self)

    def defer(self, *args, **kwargs):
        """QuerySet-compatible ``defer`` method. Will silently skip filtering
        for incompatible iterables."""
        return self._django_factory('defer', *args, **kwargs)

    def exclude(self, *args, **kwargs):
        """QuerySet-compatible ``exclude`` method. Will silently skip filtering
        for incompatible iterables."""
        return self._django_factory('exclude', *args, **kwargs)

    def exists(self):
        """QuerySet-compatible ``exists`` method. Supports multiple iterables.
        """
        return bool(len(self))

    def extra(self, *args, **kwargs):
        """QuerySet-compatible ``extra`` method. Will silently skip filtering
        for incompatible iterables."""
        return self._django_factory('extra', *args, **kwargs)

    def filter(self, *args, **kwargs):
        """QuerySet-compatible ``filter`` method. Will silently skip filtering
        for incompatible iterables."""
        return self._django_factory('filter', *args, **kwargs)

    def none(self, *args, **kwargs):
        return chain()

    def only(self, *args, **kwargs):
        """QuerySet-compatible ``only`` method. Will silently skip filtering
        for incompatible iterables."""
        return self._django_factory('only', *args, **kwargs)

    def order_by(self, *args, **kwargs):
        """QuerySet-compatible ``order_by`` method. Also supports iterables
        other than QuerySets but they need to be presorted for the chain to
        return consistently ordered results."""
        result = self._django_factory('order_by', *args, **kwargs)
        result.xsort.extend(args)
        try:
            if self.xkey() is unset:
                result.xkey = lambda v: 0
        except TypeError:
            pass
        return result

    @property
    def ordered(self):
        """``True`` if the chain is ordered — i.e. has an ``order_by()``
        clause or a default ``xkey`` ordering. ``False`` otherwise.

        Compatible with QuerySet.ordered."""
        try:
            return len(self.xsort) or self.xkey() is not unset
        except TypeError:
            return True

    def prefetch_related(self, *args, **kwargs):
        """QuerySet-compatible ``prefetch_related`` method. Will silently skip
        filtering for incompatible iterables."""
        return self._django_factory('prefetch_related', *args, **kwargs)

    def select_for_update(self, *args, **kwargs):
        """QuerySet-compatible ``select_for_update`` method. Will silently skip
        filtering for incompatible iterables."""
        return self._django_factory('select_for_update', *args, **kwargs)

    def select_related(self, *args, **kwargs):
        """QuerySet-compatible ``select_related`` method. Will silently skip
        filtering for incompatible iterables."""
        return self._django_factory('select_related', *args, **kwargs)

    def using(self, *args, **kwargs):
        """QuerySet-compatible ``using`` method. Will silently skip filtering
        for incompatible iterables."""
        return self._django_factory('using', *args, **kwargs)

    def values(self, *fields):
        """QuerySet-compatible ``values`` method. If ``fields`` are not
        specified, results from non-QuerySet-like iterables are returned as-is.
        Otherwise, each result is converted to a dictionary using the ``xvalue``
        algorithm.

        Note: if you use ``xform``, it will receive a dictionary after calling
        this method.
        """
        result = self._django_factory('values', *fields)
        if fields:
            result.xvalues_mode = dict
            result.xvalues_fields = fields
        else:
            result.xvalues_mode = None
            result.xvalues_fields = ()
        return result

    def values_list(self, *fields, **kwargs):
        """QuerySet-compatible ``values_list`` method. If ``fields`` are not
        specified, results from non-QuerySet-like iterables are returned as-is.
        Otherwise, each result is converted to a list of values using the
        ``xvalue`` algorithm.

        Note: if you use ``xform``, it will receive a list of values after
        calling this method.
        """
        flat = kwargs.pop('flat', False)
        if kwargs:
            raise TypeError('Unexpected keyword arguments to values_list: %s'
                    % (kwargs.keys(),))
        if flat and len(fields) > 1:
            raise TypeError("'flat' is not valid when values_list is called "
                            "with more than one field.")
        if fields:
            result = self.copy()
            result.xvalues_mode = tuple if flat else list
            result.xvalues_fields = fields
        else:
            result = self._django_factory('values_list', *fields)
            result.xvalues_mode = None
            result.xvalues_fields = ()
        return result
