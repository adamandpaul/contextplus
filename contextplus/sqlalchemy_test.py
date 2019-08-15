# -*- coding:utf-8 -*-

from . import sqlalchemy
from unittest import TestCase
from unittest.mock import MagicMock


class TestDomainSQLAlchemyRecord(TestCase):
    def test_from_id(self):
        cls = MagicMock()  # we mock the class so we can it as an object factory
        cls.id_fields = ("record_id",)
        parent = MagicMock()
        id = {"record_id": "blah"}

        domain = sqlalchemy.DomainSQLAlchemyRecord.from_id.__func__(
            cls, parent, "foo", id
        )

        db_session = parent.acquire.db_session
        db_session.query.assert_called_with(cls.record_type)

        q = db_session.query.return_value
        q.filter_by.assert_called_with(**id)

        q = q.filter_by.return_value
        q.one_or_none.assert_called_with()

        record = q.one_or_none.return_value
        cls.assert_called_with(parent=parent, name="foo", record=record)
        self.assertEqual(domain, cls.return_value)


class TestDomainSQLAlchemyRecordCollection(TestCase):
    def test_default_order_by_fields(self):
        collection = sqlalchemy.DomainSQLAlchemyRecordCollection()
        collection.child_type = MagicMock()
        self.assertEqual(
            collection.default_order_by_fields, collection.child_type.id_fields
        )

    def test_child_from_record(self):
        collection = sqlalchemy.DomainSQLAlchemyRecordCollection()
        collection.child_type = MagicMock()
        collection.name_from_child = MagicMock()
        record = MagicMock()
        child = collection.child_from_record(record)
        collection.child_type.assert_called_with(parent=collection, record=record)
        collection.name_from_child.assert_called_with(child)
        name = collection.name_from_child.return_value
        child.set_name.assert_called_with(name)
        self.assertEqual(child, collection.child_type.return_value)

    def test_query(self):
        collection = sqlalchemy.DomainSQLAlchemyRecordCollection()
        collection.parent = MagicMock()
        collection.child_type = MagicMock()
        query = collection.query([{"filter_by": {"record_id": "abc"}}])

        db_session = collection.acquire.db_session
        db_session.query.assert_called_with(collection.child_type.record_type)
        q = db_session.query.return_value
        q.filter_by.assert_called_with(record_id="abc")
        q = q.filter_by.return_value
        self.assertEqual(query, q)

    def test_filter(self):
        collection = sqlalchemy.DomainSQLAlchemyRecordCollection()
        collection.query = MagicMock()
        collection.child_type = MagicMock()
        collection.child_from_record = MagicMock()
        r1 = MagicMock()
        r2 = MagicMock()
        q1 = collection.query.return_value
        q2 = q1.order_by.return_value
        q3 = q2.limit.return_value
        q3.offset.return_value = [r1, r2]
        criteria = MagicMock()
        order_by = ["aaa"]
        data = collection.filter(
            criteria=criteria, order_by=order_by, limit=10, offset=20
        )
        self.assertEqual(data["total"], q1.count.return_value)
        q1.order_by.assert_called_with(collection.child_type.record_type.aaa)
        q2.limit.assert_called_with(10)
        q3.offset.assert_called_with(20)
        collection.child_from_record.assert_any_call(r1)
        collection.child_from_record.assert_any_call(r2)
        self.assertEqual(
            data["items"],
            [
                collection.child_from_record.return_value,
                collection.child_from_record.return_value,
            ],
        )

    def test_iter_children(self):
        collection = sqlalchemy.DomainSQLAlchemyRecordCollection()
        collection.query = MagicMock()
        collection.child_type = MagicMock()
        collection.child_type.id_fields = ["aaa"]
        collection.child_from_record = MagicMock()
        r1 = MagicMock()
        r2 = MagicMock()
        q1 = collection.query.return_value
        q1.order_by.return_value = [r1, r2]
        children = list(collection.iter_children())
        q1.order_by.assert_called_with(collection.child_type.record_type.aaa)
        collection.child_from_record.assert_any_call(r1)
        collection.child_from_record.assert_any_call(r2)
        self.assertEqual(
            children,
            [
                collection.child_from_record.return_value,
                collection.child_from_record.return_value,
            ],
        )
