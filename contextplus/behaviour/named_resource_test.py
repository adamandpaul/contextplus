# -*- coding:utf-8 -*-

from . import named_resource
from unittest import TestCase
from unittest.mock import MagicMock


class TestResource(TestCase):
    def test_resource(self):
        function = MagicMock()
        decorated = named_resource.resource("foo")(function)
        self.assertIsInstance(decorated, named_resource.NamedResourceFactoryDecorator)
        self.assertEqual(decorated.name, "foo")
        self.assertEqual(decorated.factory, function)


class TestNamedResourceFactoryDecorator(TestCase):
    def test_named_resource_factory_decorator(self):
        function = MagicMock()
        expected_resource = function.return_value
        expected_resource.__name__ = None
        decorated = named_resource.NamedResourceFactoryDecorator("foo", function)
        self.assertEqual(decorated.name, "foo")
        self.assertEqual(decorated.factory, function)
        instance = MagicMock()
        instance._named_resource_cache_foo = None
        new_resource = decorated.__get__(instance, None)()
        self.assertEqual(new_resource, expected_resource)
        function.assert_called_with(instance)
        expected_resource.set_name.assert_called_with("foo")


class TestNamedResourceBehaviour(TestCase):
    def setUp(self):
        class Child(object):
            pass

        class Context(named_resource.NamedResourceBehaviour):
            @named_resource.resource("foo")
            def get_foo(self):
                return Child()

            @named_resource.resource("bar")
            def get_bar(self):
                return Child()

        self.Child = Child
        self.Context = Context
        self.context = Context()

    def test_getitem(self):
        result = self.context["foo"]
        self.assertIsInstance(result, self.Child)
        self.assertEqual(result.__name__, "foo")

        result2 = self.context.get_named_resource("bar")
        self.assertIsInstance(result2, self.Child)
        self.assertEqual(result2.__name__, "bar")

        # check caching works
        result3 = self.context['foo']
        self.assertIs(result3, result)

    def test_normal_functions(self):
        result = self.context.get_foo()
        self.assertIsInstance(result, self.Child)
        self.assertEqual(result.__name__, "foo")

    def test_iter_named_resources(self):
        foo_and_bar = list(self.context.iter_named_resources())
        foo_and_bar.sort(key=lambda x: x.__name__)
        foo_and_bar[0].__name__ = "bar"
        foo_and_bar[1].__name__ = "foo"
