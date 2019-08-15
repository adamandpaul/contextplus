# -*- coding:utf-8 -*-
"""The base object is a pattern for use in creating business domain logic
centered around a URL traversal system.
"""

from .behaviours import BehaviourTinterface
from .behaviours import BehaviourTraversal
from .behaviours import BehaviourTraversalPathUtilities
from .behaviours import BehaviourWorkflow
from typing import Optional


class DomainBase(
    BehaviourTinterface,
    BehaviourTraversal,
    BehaviourWorkflow,
    BehaviourTraversalPathUtilities,
):
    """The base domain object which all domain objects inherit.

    Designed to apply common functions to all domain objects.
    """

    @classmethod
    def get_meta_title(cls) -> str:
        """A human readable title of the kind of object"""
        return cls.__name__

    name = None
    parent = None

    @property
    def title(self) -> str:
        """A human readable title of this object instance"""
        meta_title = self.get_meta_title()
        name = self.name
        if name is not None:
            return f"{meta_title}: {self.name}"
        else:
            return f"{meta_title}"

    @property
    def description(self) -> str:
        """A short description of this object"""
        return ""

    @property
    def __name__(self):
        """Return the name unless it is None.
        In which case throw an AttributeError"""
        if self.name is None:
            raise AttributeError("Name not yet set")
        return self.name

    @property
    def __parent__(self):
        """Pyramid traversal interface"""
        return self.parent

    def __init__(self, parent=None, name: Optional[str] = None):
        """Initialize the DomainBase object

        The name attribute can be set after the creation of the domain object
        by calling ``self.set_name``. The reason for this is in the case were
        the name value is a dependency of the domain interface.
        """
        self.parent = parent
        self.set_name(name)

    def set_name(self, name: str = None):
        """Allow setting the name"""
        self.name = name
