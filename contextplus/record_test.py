# -*- coding:utf-8 -*-

from . import exc
from . import record
from unittest import TestCase
from unittest.mock import MagicMock
from unittest.mock import Mock


class TestDomainRecord(TestCase):

    def setUp(self):
        db_record = MagicMock()
        db_record.record_id = 'abc'
        self.db_record = db_record

        class MyRecord(record.DomainRecord):
            id_fields = ('record_id',)
            record_type = MagicMock()

        self.record = MyRecord(record=db_record)
        self.record.acquire = MagicMock()

    def test_attributes(self):
        self.assertEqual(self.record._record, self.db_record)
        self.assertEqual(self.record.id, {'record_id': 'abc'})

    def test_edit(self):
        self.record.edit(foo='blah', bar='hello')
        self.assertEqual(self.db_record.foo, 'blah')
        self.assertEqual(self.db_record.bar, 'hello')

    def test_edit_fail(self):
        del self.record.record_type.missing
        data = ['missing', '_protected', 'record_id']
        for field_name in data:
            with self.assertRaises(exc.DomainRecordUpdateError):
                self.record.edit(**{field_name: 'foo'})

    def test_api_patch(self):
        r = self.record
        r.edit = Mock()
        r.api_patch_field_whitelist = ('foo',)
        r.api_patch(foo='bar')
        r.edit.assert_called_with(foo='bar')

    def test_api_patch_forbidden_field(self):
        r = self.record
        r.api_patch_field_whitelist = ('foo',)
        with self.assertRaises(exc.DomainForbiddenError):
            r.api_patch(size='big')
