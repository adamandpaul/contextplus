# -*- coding:utf-8 -*-

from . import base


class DomainMapping(base.DomainBase):
    """A single domain backed by a mapping object"""

    _mapping = None
    workflow_key = 'workflow_state'

    def __init__(self, parent=None, name: str = None, mapping=None):
        super().__init__(parent, name)
        self._mapping = mapping

    @property
    def workflow_state(self):
        """Return the current workflow state"""
        return self._mapping.get(self.workflow_key, None) or self.workflow_default_state
