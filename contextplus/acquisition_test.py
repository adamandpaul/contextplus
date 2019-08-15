# -*- coding:utf-8 -*-

from . import acquisition
from unittest import TestCase


class TestAcquisition(TestCase):
    def test_acquire_parent_attribute(self):
        class Root(object):
            size = "big"
            color = "red"
            shape = "oval"

        class Parent(object):
            colour = "blue"
            shape = "triangle"

        class Child(object):
            shape = "circle"

            def iter_ancestors(self):
                return [Parent(), Root()]

        acquire = acquisition.AcquisitionProxy(Child())
        self.assertEqual(acquire.shape, "circle")
        self.assertEqual(acquire.colour, "blue")
        self.assertEqual(acquire.size, "big")
        with self.assertRaises(AttributeError):
            acquire.foo

        # Check caching
        self.assertEqual(acquire.__dict__["shape"], "circle")
        self.assertEqual(acquire.__dict__["colour"], "blue")
        self.assertEqual(acquire.__dict__["size"], "big")
