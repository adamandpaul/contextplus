# -*- coding:utf-8 -*-
"""Module of resource behaviours
"""

from . import acquisition
from . import exc
from .reify import reify
from collections import OrderedDict
from typing import Iterable

import logging
import zlib


class BehaviourWorkflow(object):
    """Add workflow actions and transitions"""

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

        # Check that the transition is valid
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


class BehaviourTinterface(object):
    """Behaviour to allow item factories for a given traversal name"""

    # Traversal features - tinterfaces

    def get_tinterface(self, name: str, default=None):
        """Return an tinterface for a given name.

        tinterfaces are traversable by self[name], this function is called
        by __getitem__ to obtain the object for a given name. By default this
        function looks object factories which are marked on the class with the attribute
        tinterface_factory_for. get_tinterfaces doesn't iterate through the instance
        properties in order to prevent bringing into memory evey attribute.

        tinterface_factory_for can only be a string. For example:

            class A(DomainBase):

                def get_blahs_collection(self):
                    return Blahs()
                get_blah_collection.tinterface_factory_for = 'blahs'

        Then A()['blahs'] would be an instance of Blahs.

        Note that on successive calls a new object is returned to prevent any
        circular references occurring.

        Arguments:
            name: The name of the tinterface. This must be a string.
            default: The object to be returned if no interface was found.

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
            return super().__getitem__(key)


class BehaviourTraversalPathUtilities(object):
    """Behaviour which adds traversal path utilities to the domain object"""

    # Navigating up the tree and adding acquisition

    def iter_ancestors(self):
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
    def root(self):
        """Return the root object"""
        highest = self
        for ancestor in self.iter_ancestors():
            highest = ancestor
        return highest

    @reify
    def acquire(self):
        """Return the acquisition proxy from self"""
        return acquisition.AcquisitionProxy(self)


class AdaptComponentLoggerToLogger(object):
    """Adapt a component logger to a logging.Logger interface"""

    def __init__(self, context):
        self._context = context

    def info(self, message):
        self._context.log_info(message)


class BehaviourLegacy(object):
    """Behaviours which are potentially will be removed in the future"""

    @reify
    def title_short(self) -> str:
        """Return a shortened version of the title of this object"""
        return self.title

    @property
    def logger(self):
        """Return a logger interface"""
        logger = self.acquire.get_logger()
        if isinstance(logger, logging.Logger):
            return logger
        else:
            return AdaptComponentLoggerToLogger(logger)

    # Information Properties

    @classmethod
    def get_info_key_descriptions(cls):
        """Return human readable descriptions for info keys"""
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
        """Return information useful for the admin profile"""
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
        """Items returned from an api"""
        return {}
