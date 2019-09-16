# -*- coding:utf-8 -*-

from . import exc
from . import record
from unittest import TestCase
from unittest.mock import MagicMock


class TestRecordProperty(TestCase):
    def test_record_property(self):
        obj = MagicMock()
        result = record.record_property("foo").fget(obj)
        self.assertEqual(result, obj._record.foo)


class TestRecordItem(TestCase):
    def setUp(self):
        db_record = MagicMock()
        db_record.record_id = "abc"
        self.db_record = db_record

        class MyRecord(record.RecordItem):
            id_fields = ("record_id",)
            record_type = MagicMock()

        self.record = MyRecord(record=db_record)
        self.record.parent = MagicMock()

    def test_attributes(self):
        self.assertEqual(self.record._record, self.db_record)
        self.assertEqual(self.record.id, {"record_id": "abc"})

    def test_edit(self):
        self.record.edit(foo="blah", bar="hello")
        self.assertEqual(self.db_record.foo, "blah")
        self.assertEqual(self.db_record.bar, "hello")

    def test_edit_fail(self):
        del self.record.record_type.missing
        data = ["missing", "_protected", "record_id"]
        for field_name in data:
            with self.assertRaises(exc.RecordUpdateError):
                self.record.edit(**{field_name: "foo"})
