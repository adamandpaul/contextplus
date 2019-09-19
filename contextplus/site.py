# -*- coding:utf-8 -*-

from . import base
from .behaviour import resource_cache


class Site(resource_cache.ResourceCacheBehaviour, base.Base):
    """A site object which in most cases will be the root object
    """

    def __init__(
        self, parent=None, name: str = None, settings=None, db_session=None, redis=None
    ):
        super().__init__(parent, name)
        self.settings = settings or {}
        self.db_session = db_session
        self.redis = redis
