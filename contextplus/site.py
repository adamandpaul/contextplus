# -*- coding:utf-8 -*-

from . import base
from .reify import reify

import logging
import weakref


class Site(base.DomainBase):
    """A site object which in most cases will be the root object
    """

    logger_name = 'ap.ecommerce.app'

    def __init__(self, parent=None, name: str = None, request=None, settings=None):
        super().__init__(parent, name)
        if request is None:
            self.settings = settings
            self.get_request = lambda: None
        else:
            assert settings is None, 'settings and request can not be both set'
            self.get_request = weakref.ref(request)

    @reify
    def no_cache(self):
        return True

    @reify
    def settings(self):
        return self.get_request().registry.settings

    @reify
    def db_session(self):
        return self.get_request().db_session

    @reify
    def redis(self):
        return self.get_request().redis

    def get_logger(self):
        """Fall back logger for the entire site when get_logger is called from self.acquire"""
        return logging.getLogger(self.logger_name)
