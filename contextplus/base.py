# -*- coding:utf-8 -*-
"""The domainlib base object is a patten for use in createing business domain logic
centered around a URL travseral system.
"""

from . import acquision
from . import exc
from collections import OrderedDict
from pyramid.decorator import reify
from typing import Iterable
from typing import Optional

import logging
import zlib


class AdaptComponentLoggerToLogger(object):
    """Adapt a component logger to a logging.Logger interface"""

    def __init__(self, context):
        self._context = context

    def info(self, message):
        self._context.log_info(message)


class DomainBase(object):
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

    # Navigating up the tree and adding acquision

    def iter_ancestors(self) -> Iterable['DomainBase']:
        current = self.parent
        while current is not None:
            yield current
            current = current.parent

    @reify
    def path_names(self):
        """Return a tuple of path names"""
        items = []
        for item in sorted(list(self.iter_ancestors()), reverse=True):
            items.append(item.name)
        items.append(self.name)
        return tuple(items)

    @reify
    def path_hash(self):
        data = repr(self.path_names).encode('utf8')
        return hex(zlib.adler32(data))[2:]

    @reify
    def root(self) -> 'DomainBase':
        """Return the root object"""
        highest = self
        for ancestor in self.iter_ancestors():
            highest = ancestor
        return highest

    @reify
    def acquire(self):
        """Return the acquision proxy from self"""
        return acquision.AcquisitionProxy(self)

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

    # Traversal features - tinterfaces

    def get_tinterface(self, name: str, default=None):
        """Return an tinterface for a given name.

        tinterfaces are traversable by self[name], this function is called
        by __getitem__ to obtain the object for a given name. By defeault this
        function looks object factories which are marked on the class with the attribute
        tinterface_factory_for. get_tinterfaces doesn't iterate through the instance
        properties inorder to prevent bringing into memory evey attribute.

        tinterface_factory_for can only be a string. For example:

            class A(DomainBase):

                def get_blahs_collection(self):
                    return Blahs()
                get_blah_collection.tinterface_factory_for = 'blahs'

        Then A()['blahs'] would be an instance of Blahs.

        Note that on successive calls a new object is returned to prevent any circular references occuring.

        Arguments:
            name: The name of the tinterface. This must be a string.
            default: The object to be retuned if no tinerface was found.

        Returns:
            object: If the the tinterface is found
            None: If no tinterface is found
        """
        cls = type(self)
        for cls_name in dir(cls):
            cls_item = getattr(cls, cls_name, None)
            if cls_item is not None:
                if getattr(cls_item, 'tinterface_factory_for', None) == name:
                    factory = getattr(self, cls_name)
                    return factory()
        return default

    def iter_tinterfaces(self) -> Iterable:
        """Iterate through tinterfaces"""
        cls = type(self)
        for cls_name in dir(cls):
            cls_item = getattr(cls, cls_name, None)
            if cls_item is not None:
                if getattr(cls_item, 'tinterface_factory_for', None) is not None:
                    factory = getattr(self, cls_name)
                    tinterface = factory()
                    if tinterface is not None:
                        yield factory()

    # Traversal

    def __getitem__(self, key: str):
        """Return an items contained in this domain object.

        Raises:
            DomainTraversalKeyError: If there is not item to return
        """
        assert isinstance(key, str), 'Only string keys are supported on __getitem__'
        item = self.get_tinterface(key)
        if item is not None:
            return item
        else:
            raise exc.DomainTraversalKeyError(key)

    def get(self, key: str, default=None):
        """Convienence method to return a default value when there is a KeyError"""
        try:
            return self.__getitem__(key)
        except KeyError:
            return default

    # Workflow
    workflow_default_state = 'unknown'
    workflow_transitions = {}
    workflow_previous_state = None

    @property
    def workflow_state(self):
        return self.workflow_default_state

    def workflow_set_state(self, state):
        """Set the current workflow state"""
        # self.workflow_previous_state = self.workflow_state
        raise exc.WorkflowTransitionError('Object does not support workflow transitions')

    def workflow_action(self, action):
        """Do a workflow action on this object"""
        start_state = self.workflow_state
        transition = self.workflow_transitions.get(action, None)

        # Check that the transation is valid
        if transition is None:
            raise exc.WorkflowUnknownActionError(f'Unknown workflow action {action} on {self.title}.')
        if start_state not in transition['from']:
            raise exc.WorkflowIllegalTransitionError(f'Can not {action} on an instance of {self.__class__.__name__} in the state {start_state}')
        destination_state = transition['to']

        # Log transition
        self.logger.info(f'workflow: {action}')

        # Perform transition
        before = getattr(self, f'workflow_before_{action}', None)
        if before is not None:
            before()
        self.workflow_set_state(destination_state)
        after = getattr(self, f'workflow_after_{action}', None)
        if after is not None:
            after()

    # Logger prooperty
    @property
    def logger(self):
        """Return a logger interface"""
        logger = self.acquire.get_logger()
        if isinstance(logger, logging.Logger):
            return logger
        else:
            return AdaptComponentLoggerToLogger(logger)
