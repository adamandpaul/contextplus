# -*- coding:utf-8 -*-
"""Acquisition

Acquisition is an abstraction methodology used in traversal scenarios, by
which descendents can enquire up the ancestor chain for an object. For example
if an object wanted a database session it can acquire it from a parent through
``self.acquisition.db_session`` which could be ``self.parent.db_session`` or
``self.parent.parent.db_session`` depending where it is first found.

Item acquisition e.g. ``self.acquisition['foo']`` is specifically not
implemented since that opens the possibility of injection attacks from
content sources.
"""

from . import exc

import itertools


_MISSING_ATTRIBUTE = object()  # an object representing no returned attribute


class AcquisitionProxy(object):
    """A proxy object which searches for attributes or items from ancestors
    of the current domain object
    """

    def __init__(self, subject):
        """Initialize acquisition proxy

        Args:
            subject: The current object to start the search
        """
        self._subject = subject

    def __getattr__(self, name: str):
        nodes = itertools.chain([self._subject],
                                self._subject.iter_ancestors())
        for current in nodes:
            value = getattr(current, name, _MISSING_ATTRIBUTE)
            if value is not _MISSING_ATTRIBUTE:
                setattr(self, name, value)
                return value

        # Nothing found
        raise exc.DomainAcquisitionAttributeError(name)
