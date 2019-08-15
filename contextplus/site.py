# -*- coding:utf-8 -*-

from . import base


class Site(base.DomainBase):
    """A site object which in most cases will be the root object

    The ``logger_name`` should be overridden to something meaningful such as
    your site's name on ``Site`` subclasses.
    """

    logger_name = "contextplus"

    def __init__(
        self, parent=None, name: str = None, settings=None, db_session=None, redis=None
    ):
        super().__init__(parent, name)
        self.settings = settings or {}
        self.db_session = db_session
        self.redis = redis
