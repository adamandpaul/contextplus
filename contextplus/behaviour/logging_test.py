# -*- coding:utf-8 -*-

from . import acquisition
from . import logging
from . import traversal
from unittest import TestCase
from unittest.mock import MagicMock


class TestLogging(TestCase):
    def test_logging_from_get_logger(self):
        class Obj(
            logging.LoggingBehaviour,
            acquisition.AcquisitionBehaviour,
            traversal.TraversalBehaviour,
        ):
            pass

        o = Obj()
        o.parent = MagicMock()
        logger = o.logger
        self.assertEqual(logger, o.parent.get_logger.return_value)

    def test_logging_from_no_get_logger(self):
        class Obj(
            logging.LoggingBehaviour,
            acquisition.AcquisitionBehaviour,
            traversal.TraversalBehaviour,
        ):
            pass

        o = Obj()
        logger = o.logger
        self.assertEqual(logger, logging.default_logger)

    def test_logging_from_no_acquisition(self):
        class Obj(logging.LoggingBehaviour):
            pass

        o = Obj()
        logger = o.logger
        self.assertEqual(logger, logging.default_logger)
