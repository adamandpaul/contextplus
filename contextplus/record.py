# -*- coding:utf-8 -*-


from . import base
from . import exc
from .reify import reify


class DomainRecord(base.DomainBase):
    """A single domain record"""

    _record = None
    record_type = None
    id_fields = None

    def __init__(self, parent=None, name: str = None, record=None):
        super().__init__(parent, name)
        self._record = record

    @classmethod
    def from_id(cls, parent=None, name: str = None, id: dict = None) -> 'DomainRecord':
        """Pull a record and construct this domain object"""
        raise NotImplementedError()

    @reify
    def id(self) -> dict:
        """Return the records ID"""
        record = self._record
        value = {}
        for field_name in self.id_fields:
            value[field_name] = getattr(record, field_name)
        return value

    wtforms_record_edit_blank = None

    def wtforms_record_edit(self, data=None):
        """Return an instance of the edit from, if data is supplied then
        init the form from data"""
        if data is not None:
            return self.wtforms_record_edit_blank(data)
        else:
            return self.wtforms_record_edit_blank(obj=self._record)

    def edit(self, **kwargs):
        """Edit the values in the record"""
        id_fields = self.id_fields
        record = self._record
        record_type = self.record_type
        for key, value in kwargs.items():
            if key.startswith('_'):
                raise exc.DomainRecordUpdateError(f'Can not edit protected field: {key}')
            if key in id_fields:
                raise exc.DomainRecordUpdateError(f'Can not edit primary key field: {key}')
            if not hasattr(record_type, key):
                raise exc.DomainRecordUpdateError(f'Field not found: {key}')

            old_value = getattr(record, key)
            if old_value != value:
                setattr(record, key, value)
                self.logger.info(f'Set {key}: {value}')

    api_patch_field_whitelist = ()

    def api_patch(self, **kwargs):
        """Edit the record from an api call"""
        patch_keys_not_allowed = []
        for key in kwargs:
            if key not in self.api_patch_field_whitelist:
                patch_keys_not_allowed.append(key)
        if len(patch_keys_not_allowed) > 0:
            raise exc.DomainForbiddenError(f'Forbidden to patch keys {patch_keys_not_allowed}')
        self.edit(**kwargs)

    workflow_field = 'workflow_state'

    def workflow_set_state(self, state):
        """Set a workflow state on the record identified by workflow_field"""
        self.edit(**{self.workflow_field: state})

    @property
    def workflow_state(self):
        """Return the current workflow state"""
        return getattr(self._record, self.workflow_field, None) or self.workflow_default_state
