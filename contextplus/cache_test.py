# -*- coding:utf-8 -*-

from . import cache
from unittest import TestCase


class TestLRUCache(TestCase):
    def setUp(self):
        self.cache = cache.LRUCache(max_size=2)

    def test_lru_cache(self):
        c = self.cache
        c.set("foo", 1)
        c.set("bar", 2)
        self.assertEqual(c.get("foo"), 1)
        self.assertEqual(c.get("bar"), 2)
        c.set("blah", 3)
        self.assertEqual(c.get("blah"), 3)
        self.assertIsNone(c.get("foo"))
        c.set("bar", 4)
        self.assertEqual(c.get("bar"), 4)
        c.clear()
        [self.assertIsNone(c.get(k)) for k in ["foo", "bar", "blah"]]
