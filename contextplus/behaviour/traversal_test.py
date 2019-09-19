# -*- coding:utf-8 -*-

from . import traversal
from unittest import TestCase


class TestTraversal(TestCase):
    def setUp(self):

        self.root = traversal.TraversalBehaviour()
        self.root.name = None

        self.mid = traversal.TraversalBehaviour()
        self.mid.name = "mid"
        self.mid.parent = self.root

        self.leaf = traversal.TraversalBehaviour()
        self.leaf.name = "leaf"
        self.leaf.parent = self.mid

    def test_getitem(self):
        result = self.root.get("blah", "notfound")
        self.assertEqual(result, "notfound")

        with self.assertRaises(KeyError):
            self.root["blah"]

    def test_iter_ancestors(self):
        result = [a.name for a in self.leaf.iter_ancestors()]
        self.assertEqual(result, ["mid", None])

    def test_path_names(self):
        result = self.leaf.path_names
        self.assertEqual(result, ("", "mid", "leaf"))
        self.assertEqual(self.root.path_names, ("",))

    def test_root(self):
        result = self.leaf.root
        self.assertEqual(result, self.root)
