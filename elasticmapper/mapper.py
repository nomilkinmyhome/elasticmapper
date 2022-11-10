from typing import Collection, Dict, Optional

from elasticmapper.supported_orms import SupportedORMs
from elasticmapper.orm_mappings import (
    sqlalchemy_mapping,
    peewee_mapping,
    django_mapping,
)


class Mapper:
    _supported_orms = tuple(SupportedORMs)
    _orm_fields_mapping = {
        SupportedORMs.SQLAlchemy: sqlalchemy_mapping,
        SupportedORMs.Peewee: peewee_mapping,
        SupportedORMs.DjangoORM: django_mapping,
    }
    orm = None

    def __init__(
        self,
        model,
        keyword_fields: Optional[Collection[str]] = None,
        alternative_names: Optional[Dict[str, str]] = None,
        include: Collection[Optional[str]] = (),
        exclude: Collection[Optional[str]] = (),
        follow_nested: bool = False,
        custom_values: Optional[Dict[str, dict]] = None,
    ):
        self.model = model
        self.keyword_fields = keyword_fields
        self.alternative_names = alternative_names
        self.include = include
        self.exclude = exclude
        self.follow_nested = follow_nested
        self.custom_values = custom_values
        self.orm_mapping = self._orm_fields_mapping.get(self.orm)
        self.schema = self._get_model_columns()

    def load(self):
        self._fill_schema()
        if self.keyword_fields is not None:
            self._fill_keyword_fields()
        if self.custom_values is not None:
            self._process_custom_values()
        if self.alternative_names is not None:
            self.schema = self._rename_fields_using_alternative_names()
        return self.schema

    def _fill_schema(self):
        extra_columns = []
        for column_name, column_value in self.schema.items():
            conditions = (
                (self.exclude and column_name in self.exclude),
                (self.include and column_name not in self.include),
            )
            if any(conditions):
                extra_columns.append(column_name)
            self.schema[column_name] = self._map_field(column_name, column_value)
        self._delete_extra_columns(extra_columns)

    def _process_custom_values(self):
        for custom_key, custom_value in self.custom_values.items():
            self.schema[custom_key] = custom_value

    def _delete_extra_columns(self, columns_to_delete):
        for column in columns_to_delete:
            self.schema.pop(column)

    def _fill_keyword_fields(self):
        for column_name in self.schema.keys():
            if column_name in self.keyword_fields:
                self.schema[column_name] = {'type': 'keyword'}

    def _rename_fields_using_alternative_names(self):
        new_schema = self.schema.copy()
        for column_name, column_type in self.schema.items():
            for old_name, new_name in self.alternative_names.items():
                if column_name == old_name:
                    new_schema[new_name] = {'type': column_type['type']}
                    new_schema.pop(old_name)
        return new_schema

    def _get_model_columns(self):
        raise NotImplementedError

    def _process_foreign_keys(self, column_name):
        raise NotImplementedError

    def _map_field(self, column_name, column_value):
        raise NotImplementedError


class DjangoMapper(Mapper):
    orm = SupportedORMs.DjangoORM

    def _get_model_columns(self):
        columns = {}
        for column_name in self.model._meta.local_fields:
            columns[column_name.__dict__['name']] = column_name.get_internal_type()
        return columns

    def _process_foreign_keys(self, column_name):
        foreign_model = self.model._meta.get_field(column_name).target_field.model
        if not self.follow_nested:
            return self.orm_mapping.get(foreign_model._meta.local_fields[0].get_internal_type())
        else:
            return {
                'properties': self.__class__(
                    model=foreign_model,
                ).load(),
            }

    def _map_field(self, column_name, column_value):
        if column_value == 'ForeignKey':
            return {'type': self._process_foreign_keys(column_name)}
        else:
            return {'type': self.orm_mapping.get(column_value)}


class SQLAlchemyMapper(Mapper):
    orm = SupportedORMs.SQLAlchemy

    def _get_model_columns(self):
        columns = {}
        try:
            for column in self.model.__table__.columns:
                columns[column.name] = column.type.__class__.__visit_name__
        except AttributeError:
            for column in self.model.columns:
                columns[column.name] = column.type.__class__.__visit_name__
        return columns

    def _process_foreign_keys(self, column_name):
        column = self.model.__table__.columns.get(column_name)
        foreign_model = next(iter(column.foreign_keys)).column.table
        if not self.follow_nested:
            return self.orm_mapping.get(foreign_model.columns[0].type.__class__.__visit_name__)
        else:
            return {
                'properties': self.__class__(
                    model=foreign_model,
                ).load(),
            }

    def _map_field(self, column_name, column_value):
        try:
            column = self.model.__table__.columns.get(column_name)
        except AttributeError:
            column = self.model.columns.get(column_name)
        fks = tuple(column.foreign_keys)
        if len(fks) > 0:
            return {'type': self._process_foreign_keys(column_name)}
        else:
            return {'type': self.orm_mapping.get(column_value)}


class PeeweeMapper(Mapper):
    orm = SupportedORMs.Peewee

    def _get_model_columns(self):
        columns = {}
        for column_name, column_meta in self.model._meta.columns.items():
            columns[column_name] = column_meta.__class__.field_type
        return columns

    def _process_foreign_keys(self, column_name):
        foreign_model = self.model._meta.columns.get(column_name).rel_model
        if not self.follow_nested:
            return self.orm_mapping.get(self.model._meta.columns.get(column_name).rel_field)
        else:
            return {
                'properties': self.__class__(
                    model=foreign_model,
                ).load(),
            }

    def _map_field(self, column_name, column_value):
        if 'rel_model' in self.model._meta.columns.get(column_name).__dict__:
            return {'type': self._process_foreign_keys(column_name)}
        else:
            return {'type': self.orm_mapping.get(column_value)}
