# -*- coding:utf-8 -*-
"""The domainlib base object is a patten for use in createing business domain logic
centered around a URL travseral system.
"""

from .behaviours import BehaviourLogging
from .behaviours import BehaviourTinterface
from .behaviours import BehaviourTraversal
from .behaviours import BehaviourTraversalPathUtilities
from .behaviours import BehaviourWorkflow
from collections import OrderedDict
from pyramid.decorator import reify
from typing import Optional


class DomainBase(BehaviourTinterface, BehaviourTraversal, BehaviourWorkflow, BehaviourLogging, BehaviourTraversalPathUtilities):
    """The base domain object which all domain objects inherit.

    Designed to apply common functions to all domain objects.
    """

    _name = None

    def __init__(self, parent=None, name: Optional[str] = None):
        """Initalize the DomainBase object

        The name attribute can be set after the creation of the domain object
        by calling self.set_name. The reason for this is in the case were the name
        value is a dependency of the domain interface.
        """
        self.parent = parent
        self.set_name(name)

    # Name property

    def set_name(self, name: str = None):
        """Allow setting the name"""
        self._name = name

    @property
    def name(self):
        """Return the name unless it is None. In which case throw an AttributeError"""
        if self._name is None:
            raise AttributeError('Name not yet set')
        return self._name

    # Information Properties

    @classmethod
    def get_info_key_descriptions(cls):
        """Return human redable descriptions for info keys"""
        descriptions = OrderedDict([
            ('object_title', 'Title'),
            ('object_name', 'URL Name'),
            ('object_meta_title', 'Type'),
            ('object_description', 'Description'),
            ('object_workflow_state', 'Workflow State'),
        ])
        return descriptions

    @reify
    def info(self):
        """Return general information about the object"""
        return OrderedDict()

    @reify
    def info_admin_profile(self):
        """Return information userful for the admin profile"""
        info = OrderedDict([
            ('object_title', self.title),
            ('object_name', self.name),
            ('object_meta_title', self.get_meta_title()),
            ('object_description', self.description),
            ('object_workflow_state', self.workflow_state),
        ])
        info.update(self.info)
        return info

    @reify
    def info_admin_export(self):
        """An info dictionary for admin export. E.g. CSV file"""
        return self.info_admin_profile

    @reify
    def api_get(self):
        """Items returnd from an api"""
        return {}

    # Properties useful fro Pyramid

    @reify
    def __name__(self):
        """Pyramid traversal interface"""
        return self.name

    @reify
    def __parent__(self):
        """Pyramid traversal interface"""
        return self.parent

    # Human friendly titles descriptions

    @classmethod
    def get_meta_title(cls) -> str:
        """A human readable title of the kind of object"""
        return cls.__name__

    @reify
    def title(self) -> str:
        """A human readable title of this object instance"""
        meta_title = self.get_meta_title()
        name = self.name
        if name is not None:
            return f'{meta_title}: {self.name}'
        else:
            return f'{meta_title}'

    @reify
    def title_short(self) -> str:
        """Return a shortened version of the title of this object"""
        return self.title

    @reify
    def description(self) -> str:
        """A short description of the this object"""
        return ''
