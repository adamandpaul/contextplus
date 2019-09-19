# -*- coding:utf-8 -*-

from . import collection
from unittest import TestCase
from unittest.mock import MagicMock


class TestCollectionSet(TestCase):
    def setUp(self):

        my_child_type = MagicMock()
        my_child_type.get_meta_title.return_value = "MyCollectionItems"

        class MyCollection(collection.Collection):

            child_type = my_child_type

            def iter_children(self):
                for c in "abcdefghijklmnopqrstuvwxyz":
                    name = c * 3
                    obj = MagicMock()
                    obj.name = name
                    yield obj

        self.collection = MyCollection()

    def test_attributes(self):
        self.assertEqual(
            self.collection.get_meta_title(),
            "Collection of objects of type MyCollectionItems",
        )

    def test_get(self):
        self.assertEqual(self.collection["aaa"].name, "aaa")
        self.assertEqual(self.collection["bbb"].name, "bbb")

    def test_cache_get(self):
        self.collection.parent = MagicMock()
        self.collection.parent.parent = None
        self.collection.parent.name = None
        self.collection.parent.resource_cache_get.return_value = 'foo'
        child = self.collection['aaa']
        self.assertEqual(child, 'foo')
        self.collection.parent.resource_cache_get.assert_called_with(('', '', 'aaa'))

    def test_cache_save(self):
        self.collection.parent = MagicMock()
        self.collection.parent.parent = None
        self.collection.parent.resource_cache_get.return_value = None
        child = self.collection['aaa']
        self.collection.parent.resource_cache_save.assert_called_with(child)

    def test_filter(self):
        data = self.collection.filter(limit=2, offset=5)
        self.assertIsNone(data["total"])
        item_names = [i.name for i in data["items"]]
        self.assertEqual(item_names, ["fff", "ggg"])

    def test_filter_end(self):
        data = self.collection.filter(limit=10, offset=25)
        self.assertEqual(data["total"], 26)
        self.assertEqual(len(data["items"]), 1)
