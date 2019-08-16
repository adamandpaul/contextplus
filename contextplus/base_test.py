# -*- coding:utf-8 -*-

from . import base
from .behaviour import acquisition
from unittest import TestCase


class TestBase(TestCase):
    def test_init(self):
        domain = base.Base(None, "my-site")
        self.assertEqual(domain.parent, None)
        self.assertEqual(domain.name, "my-site")


class TestBaseNoParent(TestCase):
    def setUp(self):
        self.domain = base.Base(None, "my-site")

    def test_name(self):
        d = self.domain
        d.set_name(None)
        with self.assertRaises(AttributeError):
            d.__name__

    def test_simple_attributes(self):
        d = self.domain
        self.assertEqual(d.__name__, "my-site")
        self.assertEqual(d.__parent__, None)
        self.assertEqual(d.title, "Base: my-site")
        self.assertEqual(d.description, "")

    def test_acquire(self):
        acquire = self.domain.acquire
        self.assertIsInstance(acquire, acquisition.AcquisitionProxy)
        self.assertEqual(acquire.title, "Base: my-site")

    def test_iter_ancestors(self):
        self.assertEqual(list(self.domain.iter_ancestors()), [])

    def test_root(self):
        self.assertEqual(self.domain.root, self.domain)

    def test_getitem(self):
        with self.assertRaises(KeyError):
            self.domain["foo"]
        self.assertEqual(self.domain.get("foo"), None)
        self.assertEqual(self.domain.get("foo", 33), 33)


class TestBaseWithParent(TestCase):
    def setUp(self):
        self.parent = base.Base(None, "parent-item")
        self.child = base.Base(self.parent, "child-item")

    def test_simple_attributes(self):
        self.assertEqual(self.child.parent, self.parent)

    def test_iter_ancestors(self):
        self.assertEqual(list(self.child.iter_ancestors()), [self.parent])

    def test_root(self):
        self.assertEqual(self.child.root, self.parent)
