# -*- coding:utf-8 -*-

from . import collection
from . import mapping
from collections import OrderedDict
from pyramid.decorator import reify


class DomainGoogleSheetsRow(mapping.DomainMapping):
    """A google sheets row"""

    @reify
    def info_admin_profile(self):
        info = super().info_admin_profile
        for key, value in self._mapping.items():
            info[f'column_{key}'] = value
        return info


class DomainGoogleSheetsRowCollection(collection.DomainCollection):
    """A collection of records sourced from google sheets

    Requres a method in the acquision `cache_get`, `cache_set` and `google_sheets_api`
    """

    child_type = DomainGoogleSheetsRow
    spreadsheet_id = None
    range = 'Sheet1!A:Z'

    def name_from_child(self, child):
        raise NotImplementedError()

    def child_from_mapping(self, mapping):
        """Return the child item from a record object"""
        child = self.child_type(parent=self,
                                mapping=mapping)
        child_name = self.name_from_child(child)
        child.set_name(child_name)
        return child

    def get_value_range(self):
        cache_key = f'{self.path_hash}:value_range'
        result = self.acquire.cache_get(cache_key)
        if result is not None:
            return result
        api = self.acquire.google_sheets_api
        value_range = api.spreadsheets().values().get(
            spreadsheetId=self.spreadsheet_id,
            range=self.range,
            valueRenderOption='FORMATTED_VALUE',
            dateTimeRenderOption='FORMATTED_STRING',
        ).execute()
        self.acquire.cache_set(cache_key, value_range)
        return value_range

    def iter_mappings_from_value_range(self, value_range):
        values = value_range.get('values', None)
        if values is None:
            raise ValueError('No values')
        if len(values) < 1:
            raise ValueError('No header row found')
        header_row = values[0]
        for row in values[1:]:
            row = row + ([None] * (len(header_row) - len(row)))
            mapping = OrderedDict()
            for k, v in zip(header_row, row):
                mapping[k] = v
            yield mapping

    def iter_children(self):
        value_range = self.get_value_range()
        mappings = self.iter_mappings_from_value_range(value_range)
        for mapping_ in mappings:
            yield self.child_from_mapping(mapping_)
