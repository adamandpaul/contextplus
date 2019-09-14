# -*- coding:utf-8 -*-


import logging


default_logger = logging.getLogger("contextplus.behaviour.logging.default_logger")


class LoggingBehaviour(object):

    _logger = None

    @property
    def logger(self):
        if self._logger is not None:
            return self._logger
        try:
            get_logger = self.acquire.get_logger
        except AttributeError:

            def get_logger():
                return default_logger

        self._logger = get_logger()  # cache the logger object on this property
        return self._logger
