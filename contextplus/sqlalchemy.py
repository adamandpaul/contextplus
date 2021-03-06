# -*- coding:utf-8 -*-

from . import collection
from . import exc
from . import record
from typing import Iterable

import sqlalchemy


class SQLAlchemyItem(record.RecordItem):
    """A Domain backed by an SQLAlchemy Record"""

    @classmethod
    def from_id(cls, parent=None, name=None, id=None):
        """
        Args:
            parent (object): The parent object
            name (str): The traversal name to get to this object
            id (dict): The id of the object as a dictionary

        Returns:
            the domain object for a given record id or None if it doesn't exist

        Raises:
            RecordIdTypeError: If the id fields don't match cls.id_fields
        """
        assert id is not None
        if set(id) != set(cls.id_fields):
            raise exc.RecordIdTypeError(
                f"Can not retrieve record from invalid id: {id}"
            )
        db_session = parent.acquire.db_session
        result = db_session.query(cls.record_type).filter_by(**id).one_or_none()
        if result is None:
            return None
        else:
            return cls(parent=parent, name=name, record=result)


class SQLAlchemyCollection(collection.Collection):
    """A collection of SQLAlchemy Records"""

    child_type = None

    @property
    def default_order_by_fields(self):
        """Return the default item order"""
        return self.child_type.id_fields

    def name_from_child(self, child):
        raise NotImplementedError()

    def child_from_record(self, child_record):
        """Return the child item from a record object"""
        child = self.child_type(parent=self, record=child_record)
        child_name = self.name_from_child(child)
        child.set_name(child_name)
        return child

    def id_from_name(self, name: str) -> dict:
        """Return the id from a name"""
        raise NotImplementedError()

    def query(self, criteria: list = []):
        """Return an SQLAlchemy query object selecting the given criteria"""

        # construct query
        db_session = self.acquire.db_session
        query = db_session.query(self.child_type.record_type)

        # apply any filters
        for criteria_part in criteria:
            if criteria_part["type"] == "filter_by":
                field_name = criteria_part["field"]
                field_value = criteria_part["value"]
                query = query.filter_by(**{field_name: field_value})
            elif criteria_part["type"] == "sub_string":
                field_name = criteria_part["field"]
                field = getattr(self.child_type.record_type, field_name)
                sub_string = criteria_part["value"]
                sub_string = sub_string.lower()
                query = query.filter(
                    sqlalchemy.func.lower(field).contains(sub_string)
                )
            else:
                raise exc.CollectionUnsupportedCriteria(
                    f"Unsupported criteria {criteria_part['type']}"
                )

        return query

    def filter(
        self,
        criteria: list = [],
        order_by: list = None,
        limit: int = None,
        offset: int = None,
    ) -> dict:
        """Return a filtered set of results"""

        query = self.query(criteria)

        # Get total records in filter
        total = query.count()

        # set record order
        record_type = self.child_type.record_type
        if order_by is None:
            order_by = self.default_order_by_fields
        for expression in order_by:
            field_name = expression.split(" ")[0]
            field = getattr(record_type, field_name)
            if expression.endswith(" desc"):
                field = field.desc()
            query = query.order_by(field)

        # set limit and offset paramitors
        if limit is not None:
            query = query.limit(limit)
        if offset is not None:
            query = query.offset(offset)

        # Iterate yielding children
        items = []
        for rec in query:
            child = self.child_from_record(rec)
            items.append(child)

        return {"total": total, "items": items}

    def iter_children(self) -> Iterable:
        """Iterate through all the children"""

        # Get query and set order
        query = self.query()
        record_type = self.child_type.record_type
        for expression in self.default_order_by_fields:
            field_name = expression.split(" ")[0]
            field = getattr(record_type, field_name)
            if expression.endswith(" desc"):
                field = field.desc()
            query = query.order_by(field)

        for rec in query:
            yield self.child_from_record(rec)

    def get_child(self, name: str, default: object = None):
        """Return a domain sql alchemy record from the given name"""
        try:
            id = self.id_from_name(name)
        except TypeError:
            return None
        child = self.child_type.from_id(parent=self, name=name, id=id)
        return child or default

    def add(self, **kwargs):
        """Create a new item"""
        record = self.child_type.record_type(**kwargs)
        db_session = self.acquire.db_session
        db_session.add(record)
        child = self.child_from_record(record)
        child.emit("created")
        return child
