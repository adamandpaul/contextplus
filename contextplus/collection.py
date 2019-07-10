# -*- coding:utf-8 -*-

from . import base
from . import exc
from typing import Iterable

import csv
import wtforms


class WTFormsCollectionCriteria(wtforms.Form):
    """An empty filter factory"""


class WTFormsCollectionAdd(wtforms.Form):
    """An empty form adder"""


class DomainCollection(base.DomainBase):
    """A collection of objects usually contentish which can be traversed by name. By default the collection is empty.
    """

    child_type = None
    wtforms_collection_criteria = WTFormsCollectionCriteria
    wtforms_collection_add = None

    @classmethod
    def get_meta_title(cls) -> str:
        """A meta title of this kind of object"""
        child_type_meta_title = cls.child_type.get_meta_title()
        return f'Collection of objects of type {child_type_meta_title}'

    def iter_children(self) -> Iterable:
        """Iterate through the children of this collection"""
        raise exc.DomainCollectionNotListable()

    def criteria_from_wtforms_collection_criteria(self, criteria_form):
        """Translate a wtform to a criteria"""
        return []

    def filter(self, criteria: list = None, limit: int = None, offset: int = None) -> Iterable:
        """Return a filtered set of results.

        This implementation is very inefficient for big sets.

        Args:
            criteria: This is up to subclasses to implement
            limit: The maximum items to return
            offset: Used to calculate the offset together with the page size

        Raises:
            DomainCollectionUnsupportedCriteria: If criteria is given.
            This is up to subclasses to implement
        """
        if criteria is None:
            criteria = []
        if len(criteria) > 0:
            raise exc.DomainCollectionUnsupportedCriteria()

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

        return {
            'total': total,
            'items': items,
        }

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
        except KeyError:
            child = self.get_child(key)
            if child is not None:
                return child
        raise exc.DomainTraversalKeyError(key)

    def add(self, **kwargs):
        """Add a new item"""
        raise NotImplementedError()

    api_post_field_whitelist = ()

    def api_post(self, **kwargs):
        """Add a new item from an api call"""
        post_keys_not_allowed = []
        for key in kwargs:
            if key not in self.api_post_field_whitelist:
                post_keys_not_allowed.append(key)
        if len(post_keys_not_allowed) > 0:
            raise exc.DomainForbiddenError(f'Forbidden to post data. Keys not allowed: {post_keys_not_allowed}')
        return self.add(**kwargs)

    def write_csv(self, stream):
        field_names = self.child_type.get_info_key_descriptions().keys()
        writer = csv.DictWriter(stream, fieldnames=field_names)
        writer.writeheader()
        for child in self.iter_children():
            writer.writerow(child.info_admin_export)
