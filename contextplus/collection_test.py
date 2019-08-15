# -*- coding:utf-8 -*-

from . import collection
from . import exc
from unittest import TestCase
from unittest.mock import MagicMock
from unittest.mock import Mock


class TestCollectionSet(TestCase):
    def setUp(self):

        my_child_type = MagicMock()
        my_child_type.get_meta_title.return_value = "MyCollectionItems"

        class MyCollection(collection.DomainCollection):

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
        self.assertIsNotNone(self.collection.wtforms_collection_criteria)

    def test_get(self):
        self.assertEqual(self.collection["aaa"].name, "aaa")
        self.assertEqual(self.collection["bbb"].name, "bbb")

    def test_filter(self):
        data = self.collection.filter(limit=2, offset=5)
        self.assertIsNone(data["total"])
        item_names = [i.name for i in data["items"]]
        self.assertEqual(item_names, ["fff", "ggg"])

    def test_filter_end(self):
        data = self.collection.filter(limit=10, offset=25)
        self.assertEqual(data["total"], 26)
        self.assertEqual(len(data["items"]), 1)

    def test_criteria_from_wtforms_collection_criteria(self):
        self.assertEqual(
            self.collection.criteria_from_wtforms_collection_criteria(None), []
        )

    def test_api_post(self):
        c = self.collection
        c.add = Mock()
        c.api_post_field_whitelist = ("foo",)
        c.api_post(foo="bar")
        c.add.assert_called_with(foo="bar")

    def test_api_post_forbidden_field(self):
        c = self.collection
        c.api_post_field_whitelist = ("foo",)
        with self.assertRaises(exc.DomainForbiddenError):
            c.api_post(size="big")
