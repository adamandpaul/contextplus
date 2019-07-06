# -*- coding:utf-8 -*-
"""Module of resource behaviours
"""

import logging


class AdaptComponentLoggerToLogger(object):
    """Adapt a component logger to a logging.Logger interface"""

    def __init__(self, context):
        self._context = context

    def info(self, message):
        self._context.log_info(message)


class BehaviourLogging(object):
    """Facility for a domain object to log information"""

    @property
    def logger(self):
        """Return a logger interface"""
        logger = self.acquire.get_logger()
        if isinstance(logger, logging.Logger):
            return logger
        else:
            return AdaptComponentLoggerToLogger(logger)
