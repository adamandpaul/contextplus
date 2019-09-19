# -*- coding:utf-8 -*-

from . import resource_cache
from unittest import TestCase
from unittest.mock import MagicMock
from unittest.mock import patch


class TestResourceCacheBehaviour(TestCase):
    class Resource(resource_cache.ResourceCacheBehaviour):
        pass

    def setUp(self):
        self.resource = self.Resource()

    @patch("cachetools.LRUCache")
    def test_cache(self, LRUCache):
        cache = LRUCache.return_value
        self.assertEqual(self.resource.resource_cache, cache)
        result = self.resource.resource_cache_get("foo")
        self.assertEqual(result, cache.get.return_value)
        obj = MagicMock()
        result = self.resource.resource_cache_save(obj)
        cache.__setitem__.assert_called_with(obj.path_names, obj)
        self.assertEqual(result, obj.path_names)
        self.resource.resource_cache_clear()
        self.assertIsNone(self.resource._resource_cache)
