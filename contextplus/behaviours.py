# -*- coding:utf-8 -*-
"""Module of resource behaviours
"""

from . import exc
from typing import Iterable

import logging


class AdaptComponentLoggerToLogger(object):
    """Adapt a component logger to a logging.Logger interface"""

    def __init__(self, context):
        self._context = context

    def info(self, message):
        self._context.log_info(message)


class BehaviourLogging(object):
    """Facility for a domain object to log information"""

    @property
    def logger(self):
        """Return a logger interface"""
        logger = self.acquire.get_logger()
        if isinstance(logger, logging.Logger):
            return logger
        else:
            return AdaptComponentLoggerToLogger(logger)


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


class BehaviourTinterface(object):
    """Behaviour to allow item factories for a given traversal name"""

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
