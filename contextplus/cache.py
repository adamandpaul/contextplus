# -*- coding:utf-8 -*-

PREV, NEXT, KEY, ITEM = 0, 1, 2, 3  # names for the link fields


class LRUCache(object):
    """Lifed mostly from Python's functools.lru_cache"""

    def __init__(self, max_size=100):
        self.max_size = max_size
        self.clear()

    def clear(self):
        """Clear the cache and cache statistics"""
        self.cache = {}
        self.root = []
        self.root[:] = [self.root, self.root, None, None]
        self.hits = 0
        self.misses = 0
        self.full = False

    def get(self, key):
        """Return an item in the cache"""
        link = self.cache.get(key)
        if link is not None:
            # Move the link to the front of the circular queue
            link_prev, link_next, _key, item = link
            link_prev[NEXT] = link_next
            link_next[PREV] = link_prev
            last = self.root[PREV]
            last[NEXT] = self.root[PREV] = link
            link[PREV] = last
            link[NEXT] = self.root
            self.hits += 1
            return item
        self.misses += 1
        return None

    def set(self, key, item):
        """Set an item in the cache"""
        if self.full:
            # Use the old root to store the new key and result.
            oldroot = self.root
            oldroot[KEY] = key
            oldroot[ITEM] = item
            # Empty the oldest link and make it the new root.
            # Keep a reference to the old key and old result to
            # prevent their ref counts from going to zero during the
            # update. That will prevent potentially arbitrary object
            # clean-up code (i.e. __del__) from running while we're
            # still adjusting the links.
            self.root = oldroot[NEXT]
            oldkey = self.root[KEY]
            self.root[KEY] = self.root[ITEM] = None
            # Now update the cache dictionary.
            del self.cache[oldkey]
            # Save the potentially reentrant cache[key] assignment
            # for last, after the root and links have been put in
            # a consistent state.
            self.cache[key] = oldroot
        else:
            # Put result in a new link at the front of the queue.
            last = self.root[PREV]
            link = [last, self.root, key, item]
            last[NEXT] = self.root[PREV] = self.cache[key] = link
            # Use the cache_len bound method instead of the len() function
            # which could potentially be wrapped in an lru_cache itself.
            self.full = len(self.cache) >= self.max_size
