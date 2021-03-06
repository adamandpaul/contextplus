# -*- coding:utf-8 -*-
"""The base object is a pattern for use in creating business domain logic
centered around a URL traversal system.
"""

from .behaviour.acquisition import AcquisitionBehaviour
from .behaviour.events import EventsBehaviour
from .behaviour.logging import LoggingBehaviour
from .behaviour.named_resource import NamedResourceBehaviour
from .behaviour.traversal import TraversalBehaviour


class Base(
    LoggingBehaviour,
    EventsBehaviour,
    NamedResourceBehaviour,
    AcquisitionBehaviour,
    TraversalBehaviour,
):
    """The base domain object which all domain objects inherit.

    Designed to apply common functions to all domain objects.
    """

    @classmethod
    def get_meta_title(cls):
        """A human readable title of the kind of object"""
        return cls.__name__

    name = None
    parent = None

    @property
    def title(self):
        """A human readable title of this object instance"""
        meta_title = self.get_meta_title()
        name = self.name
        if name is not None:
            return f"{meta_title}: {self.name}"
        else:
            return f"{meta_title}"

    @property
    def description(self):
        """A short description of this object"""
        return ""

    @property
    def __name__(self):
        """Return the name unless it is None.
        In which case throw an AttributeError"""
        return self.name

    @property
    def __parent__(self):
        """Pyramid traversal interface"""
        return self.parent

    def __init__(self, parent=None, name=None):
        """Initialize the DomainBase object

        The name attribute can be set after the creation of the domain object
        by calling ``self.set_name``. The reason for this is in the case were
        the name value is a dependency of the domain interface.
        """
        self.parent = parent
        self.set_name(name)

    def set_name(self, name=None):
        """Allow setting the name"""
        self.name = name

    def __repr__(self):
        module = self.__class__.__module__
        class_name = self.__class__.__name__
        hex_id = hex(id(self))
        path = '/'.join(self.path_names) or '/'
        return f'<{module}.{class_name} object at {hex_id} {path}>'
