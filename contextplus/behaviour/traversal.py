# -*- coding:utf-8 -*-

from .. import exc


class TraversalBehaviour(object):

    parent = None

    def __getitem__(self, key):
        """Return an items contained in this domain object.

        Raises:
            DomainTraversalKeyError: If there is not item to return
        """
        raise exc.TraversalKeyError(key)

    def get(self, key: str, default=None):
        """Convenience method to return a default value when there is a KeyError"""
        try:
            return self.__getitem__(key)
        except KeyError:
            return default

    def iter_ancestors(self):
        current = self.parent
        while current is not None:
            yield current
            current = current.parent

    @property
    def path_names(self):
        """Return a tuple of path names"""
        items = [self.name or ""]
        for ancestor in self.iter_ancestors():
            items.append(ancestor.name or "")
        items.reverse()
        return tuple(items)

    @property
    def root(self):
        """Return the root object"""
        highest = self
        for ancestor in self.iter_ancestors():
            highest = ancestor
        return highest
