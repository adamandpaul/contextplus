# -*- coding:utf-8 -*-

from . import site
from unittest import TestCase


class TestSite(TestCase):
    def test_init(self):
        db_session = object()
        redis = object()
        s = site.Site(
            None, "ACMY Foo", settings={"a": 1}, db_session=db_session, redis=redis
        )
        self.assertEqual(s.name, "ACMY Foo")
        self.assertEqual(s.settings, {"a": 1})
        self.assertEqual(s.db_session, db_session)
        self.assertEqual(s.redis, redis)
