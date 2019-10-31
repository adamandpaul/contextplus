# -*- coding:utf-8 -*-


from . import base
from . import exc


def record_property(name):
    """A read only record property proxy.

    Example::
        class Obj(...):
            foo = record_propery('foo')
    """

    @property
    def prop(self):
        return getattr(self._record, name)

    return prop


class RecordItem(base.Base):
    """A single domain record"""

    _record = None
    record_type = None
    id_fields = None

    def __init__(self, parent=None, name: str = None, record=None):
        super().__init__(parent, name)
        self._record = record

    @classmethod
    def from_id(cls, parent=None, name=None, id=None):
        """Pull a record and construct this domain object"""
        raise NotImplementedError()

    @property
    def id(self) -> dict:
        """Return the records ID"""
        record = self._record
        value = {}
        for field_name in self.id_fields:
            value[field_name] = getattr(record, field_name)
        return value

    def edit(self, **kwargs):
        """Edit the values in the record"""
        id_fields = self.id_fields
        record = self._record
        record_type = self.record_type
        self.emit("before-edit", {"kwargs": kwargs})
        changes = {}
        for key, value in kwargs.items():
            if key.startswith("_"):
                raise exc.RecordUpdateError(f"Can not edit protected field: {key}")
            if key in id_fields:
                raise exc.RecordUpdateError(f"Can not edit primary key field: {key}")
            if not hasattr(record_type, key):
                raise exc.RecordUpdateError(f"Field not found: {key}")

            old_value = getattr(record, key)
            if old_value != value:
                setattr(record, key, value)
                changes[key] = {
                    "old": old_value,
                    "new": value,
                }
        self.emit("after-edit", {
            "kwargs": kwargs,
            "changes": changes,
        })

    workflow_field = "workflow_state"

    def workflow_set_state(self, state):
        """Set a workflow state on the record identified by workflow_field"""
        self.edit(**{self.workflow_field: state})

    @property
    def workflow_state(self):
        """Return the current workflow state"""
        return (
            getattr(self._record, self.workflow_field, None)
            or self.workflow_default_state
        )
