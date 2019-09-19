# -*- coding:utf-8 -*-

from . import base
from . import exc


class Collection(base.Base):
    """A collection of objects, usually contentish, which can be
    traversed by name. By default the collection is empty.
    """

    child_type = None

    @classmethod
    def get_meta_title(cls):
        """A meta title of this kind of object"""
        child_type_meta_title = cls.child_type.get_meta_title()
        return f"Collection of objects of type {child_type_meta_title}"

    def iter_children(self):
        """Iterate through the children of this collection"""
        raise exc.CollectionNotListable()

    def filter(self, criteria=None, limit=None, offset=None):
        """Return a filtered set of results.

        This implementation is very inefficient for big sets.

        Args:
            criteria (list): This is up to subclasses to implement
            limit (int): The maximum items to return
            offset (int): Used to calculate the offset together with the page size

        Raises:
            DomainCollectionUnsupportedCriteria: If criteria is given.
            This is up to subclasses to implement
        """
        if criteria is None:
            criteria = []
        if len(criteria) > 0:
            raise exc.CollectionUnsupportedCriteria()

        total = None
        count = 0

        children = self.iter_children()

        if offset is not None:
            try:
                for i in range(offset):
                    next(children)
                    count += 1
            except StopIteration:
                total = count

        if limit is not None:
            items = []
            try:
                for i in range(limit):
                    items.append(next(children))
                    count += 1
            except StopIteration:
                total = count
        else:
            items = [c for c in children]

        return {"total": total, "items": items}

    def get_child(self, name: str, default: object = None):
        """Return a child object of this collection"""
        for child in self.iter_children():
            if child.name == name:
                return child
        return default

    def __getitem__(self, key: str):
        """Return the parent getitem otherwise check if get_child has an item

        Raises:
            KeyError: When nothing can be found
        """
        try:
            return super().__getitem__(key)
        except KeyError as err:
            try:
                child_path_names = self.path_names + (key,)
                cached_child = self.acquire.resource_cache_get(child_path_names)
            except AttributeError:
                cached_child = None
            if cached_child is not None:
                return cached_child
            child = self.get_child(key)
            if child is not None:
                try:
                    self.acquire.resource_cache_save(child)
                except AttributeError:
                    pass
                return child
            raise exc.TraversalKeyError(key) from err
