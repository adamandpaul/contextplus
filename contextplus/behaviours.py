# -*- coding:utf-8 -*-
"""Module of resource behaviours
"""

from . import acquisition
from . import exc

import zlib


class BehaviourTraversal(object):
    """Behaviour to allow items to be traversed"""

    def __getitem__(self, key: str):
        """Return an items contained in this domain object.

        Raises:
            DomainTraversalKeyError: If there is not item to return
        """
        raise exc.DomainTraversalKeyError(key)

    def get(self, key: str, default=None):
        """Convenience method to return a default value when there is a KeyError"""
        try:
            return self.__getitem__(key)
        except KeyError:
            return default


class BehaviourTraversalPathUtilities(object):
    """Behaviour which adds traversal path utilities to the domain object"""

    # Navigating up the tree and adding acquisition

    def iter_ancestors(self):
        current = self.parent
        while current is not None:
            yield current
            current = current.parent

    @property
    def path_names(self):
        """Return a tuple of path names"""
        items = []
        for item in sorted(list(self.iter_ancestors()), reverse=True):
            items.append(item.name)
        items.append(self.name)
        return tuple(items)

    @property
    def path_hash(self):
        data = repr(self.path_names).encode("utf8")
        return hex(zlib.adler32(data))[2:]

    @property
    def root(self):
        """Return the root object"""
        highest = self
        for ancestor in self.iter_ancestors():
            highest = ancestor
        return highest

    @property
    def acquire(self):
        """Return the acquisition proxy from self"""
        return acquisition.AcquisitionProxy(self)


class AdaptComponentLoggerToLogger(object):
    """Adapt a component logger to a logging.Logger interface"""

    def __init__(self, context):
        self._context = context

    def info(self, message):
        self._context.log_info(message)
