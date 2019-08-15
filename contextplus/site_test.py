# -*- coding:utf-8 -*-

from . import site
from unittest import TestCase
from unittest.mock import MagicMock


class TestSite(TestCase):
    def test_init(self):
        s = site.Site()
        self.assertEqual(s.get_request(), None)

        request = MagicMock()
        s = site.Site(request=request)
        self.assertIs(s.get_request(), request)

    def test_properties(self):
        r = MagicMock()
        s = site.Site(request=r)
        self.assertEqual(s.no_cache, True)
        self.assertEqual(s.settings, r.registry.settings)
        self.assertEqual(s.db_session, r.db_session)
        self.assertEqual(s.redis, r.redis)
