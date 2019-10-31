# -*- coding:utf-8 -*-

from . import events
from unittest import TestCase
from unittest.mock import MagicMock
from unittest.mock import patch


class TestEvent(TestCase):
    def setUp(self):
        self.target = MagicMock()
        self.event = events.Event(self.target, "click", {"type": "mouse"})

    def test_props(self):
        self.assertEqual(self.event.target, self.target)
        self.assertEqual(self.event.name, "click")
        self.assertEqual(self.event.data, {"type": "mouse"})


class TestHandlerDecorator(TestCase):
    def setUp(self):
        self.handler = MagicMock()
        self.decorated = events.HandlerDecorator(name="click", handler=self.handler)

    def test_match_success(self):
        event = MagicMock()
        event.name = "click"
        self.assertTrue(self.decorated.match(event))

    def test_match_fail(self):
        event = MagicMock()
        event.name = "resize"
        self.assertFalse(self.decorated.match(event))

    def test_get_non_instance(self):
        result = self.decorated.__get__(None, None)
        self.assertIs(result, self.decorated)

    def test_get_handler(self):
        instance = MagicMock()
        result = self.decorated.__get__(instance, None)
        result(1, 2, 3)
        self.handler.assert_called_with(instance, 1, 2, 3)


class TestHandle(TestCase):
    def test_handle(self):
        function = MagicMock()
        decorated = events.handle("foo")(function)
        self.assertIsInstance(decorated, events.HandlerDecorator)
        self.assertEqual(decorated.name, "foo")
        self.assertEqual(decorated.handler, function)


class TestEventsBehaviour(TestCase):
    def setUp(self):

        self.resize_handler = resize_handler = MagicMock(return_value="from resize")
        self.click_handler = click_handler = MagicMock(return_value="from click")
        self.acquire = MagicMock()

        self.parent_handler = MagicMock(return_value="from parent click")
        self.parent_handler_decorator = events.HandlerDecorator(
            handler=self.parent_handler, name="click", priority=None
        )
        self.acquire.event_handlers = [
            (self.parent_handler_decorator, self.parent_handler)
        ]

        class Context(events.EventsBehaviour):
            handle_resize = events.handle("resize")(resize_handler)
            handle_click = events.handle("click", priority=1)(click_handler)
            acquire = self.acquire

        self.context = Context()

    def test_event_handlers(self):
        handlers = list(self.context.event_handlers)
        handler_name_matches = [d.name for d, h in handlers]
        handler_results = [h() for d, h in handlers]
        self.assertEqual(handler_name_matches, ["click", "resize", "click"])
        self.assertEqual(
            handler_results, ["from click", "from resize", "from parent click"]
        )

    @patch("contextplus.behaviour.events.Event")
    def test_emit_handled(self, Event):
        expected_event = Event.return_value
        decorated = MagicMock()
        decorated.match.return_value = True
        bound_handler = MagicMock()
        self.context._event_handlers = [(decorated, bound_handler)]
        self.context.emit("click", {"foo": "blah"})
        Event.assert_called_with(self.context, "click", {"foo": "blah"})
        decorated.match.assert_called_with(expected_event)
        bound_handler.assert_called_with(expected_event)

    @patch("contextplus.behaviour.events.Event")
    def test_emit_not_handled(self, Event):
        decorated = MagicMock()
        decorated.match.return_value = False
        bound_handler = MagicMock()
        self.context._event_handlers = [(decorated, bound_handler)]
        self.context.emit("click")
        bound_handler.assert_not_called()
