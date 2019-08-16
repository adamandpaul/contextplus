# -*- coding:utf-8 -*-

from .. import exc


class WorkflowBehaviour(object):
    """Add workflow actions and transitions"""

    # Workflow
    workflow_default_state = "unknown"
    workflow_transitions = {}
    workflow_previous_state = None

    @property
    def workflow_state(self):
        return self.workflow_default_state

    def workflow_set_state(self, state):
        """Set the current workflow state"""
        raise NotImplementedError("Workflow set state not implemented")

    def workflow_action(self, action):
        """Do a workflow action on this object"""
        from_state = self.workflow_state
        transition = self.workflow_transitions.get(action, None)

        # Check that the transition is valid
        if transition is None:
            raise exc.WorkflowUnknownActionError(
                f"Unknown workflow action {action} on an instance of {self.__class__.__name__}."
            )
        if from_state not in transition["from"]:
            raise exc.WorkflowIllegalTransitionError(
                f"Can not {action} on an instance of {self.__class__.__name__} in the state {from_state}"
            )
        to_state = transition["to"]

        # Perform transition
        event = {"action": action, "from_state": from_state, "to_state": to_state}
        before = getattr(self, f"workflow_before_{action}", None)
        if before is not None:
            before(event)
        self.workflow_set_state(to_state)
        after = getattr(self, f"workflow_after_{action}", None)
        if after is not None:
            after(event)
