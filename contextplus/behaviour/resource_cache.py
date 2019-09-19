# -*- coding:utf-8 -*-

import cachetools


class ResourceCacheBehaviour(object):

    resource_cache_max_size = 10000
    _resource_cache = None

    @property
    def resource_cache(self):
        c = self._resource_cache
        if c is None:
            c = self._resource_cache = cachetools.LRUCache(maxsize=self.resource_cache_max_size)
        return c

    def resource_cache_get(self, key):
        return self.resource_cache.get(key)

    def resource_cache_save(self, resource):
        key = resource.path_names
        self.resource_cache[key] = resource
        return key

    def resource_cache_clear(self):
        self._resource_cache = None
