# -*- coding:utf-8 -*-
"""Acquision

Acquision is an abstraction metholodgy used in traversal sceinarios. By which
decendents can enquire up the acenstor chain for an object. For example if an object
wanted a datbase session it can acquire it from a parent through self.acquision.dbsession
which could be self.parent.dbsession or self.parent.parent.dbsession depending where
it is first found.

Item acquisition e.g. self.acquision['foo'] is specificly not implemented since that opens the
possiblity of injection attacks from content sources.
"""

from . import exc

import itertools


_MISSING_ATTRIBUTE = object()  # an object representing no returned attribute


class AcquisitionProxy(object):
    """A proxy object which searches for attributes or items from ancestors of the current
    domain object
    """

    def __init__(self, subject):
        """Initalize acquisiion proxy

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
