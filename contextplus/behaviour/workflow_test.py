# -*- coding:utf-8 -*-

from .. import exc
from . import workflow
from unittest import TestCase
from unittest.mock import Mock


class TestWorkflow(TestCase):
    def setUp(self):
        self.instance = workflow.WorkflowBehaviour()

    def test_workflow_state(self):
        self.instance.workflow_default_state = "green"
        self.assertEqual(self.instance.workflow_state, "green")

    def test_workflow_set_state(self):
        with self.assertRaises(NotImplementedError):
            self.instance.workflow_set_state("foo")

    def test_workflow_action(self):
        with self.assertRaises(exc.WorkflowUnknownActionError):
            self.instance.workflow_action("foo")


class TestMockWorkflow(TestCase):
    class MockWorkflow(workflow.WorkflowBehaviour):

        workflow_transitions = {
            "publish": {"from": ["draft", "private"], "to": "public"}
        }

        workflow_state = "private"

        def workflow_set_state(self, state):
            self.workflow_state = state

    def setUp(self):
        self.instance = self.MockWorkflow()
        self.instance.emit = Mock()

    def test_publish(self):
        self.instance.workflow_action("publish")
        self.assertEqual(self.instance.workflow_state, "public")
        expected_event_data = {
            "action": "publish",
            "from_state": "private",
            "to_state": "public",
        }
        self.instance.emit.assert_any_call(
            "workflow-before-publish", expected_event_data
        )
        self.instance.emit.assert_any_call(
            "workflow-after-publish", expected_event_data
        )
