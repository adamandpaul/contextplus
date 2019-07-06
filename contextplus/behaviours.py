# -*- coding:utf-8 -*-
"""Module of resource behaviours
"""

from . import exc

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
