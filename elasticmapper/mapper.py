from typing import Collection, Dict, Optional

from elasticmapper.supported_orms import SupportedORMs
from elasticmapper.orm_mappings import (
    sqlalchemy_mapping,
    peewee_mapping,
    django_mapping,
)

FOREIGN_KEYS_FIELDS_NAMES = ('ForeignKey',)


class Mapper:
    _supported_orms = tuple(SupportedORMs)
    _orm_fields_mapping = {
        SupportedORMs.SQLAlchemy: sqlalchemy_mapping,
        SupportedORMs.Peewee: peewee_mapping,
        SupportedORMs.DjangoORM: django_mapping,
    }

    def __init__(
        self,
        model,
        orm: Optional[SupportedORMs],
        keyword_fields: Optional[Collection[str]] = None,
        alternative_names: Optional[Dict[str, str]] = None,
        include: Collection[Optional[str]] = (),
        exclude: Collection[Optional[str]] = (),
        follow_nested: bool = False,
    ):
        self.model = model
        self.orm = orm
        self.keyword_fields = keyword_fields
        self.alternative_names = alternative_names
        self.include = include
        self.exclude = exclude
        self.follow_nested = follow_nested
        self.orm_mapping = self._orm_fields_mapping.get(orm)
        self.schema = self._get_model_columns()

        if orm not in self._supported_orms:
            raise RuntimeError(f'ORM is not supported yet. '
                               f'Supported ORMs: {[value for _, value in self._supported_orms]}')

    def load(self):
        self._fill_schema()
        if self.keyword_fields is not None:
            self._fill_keyword_fields()
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
            if column_value in FOREIGN_KEYS_FIELDS_NAMES:
                self.schema[column_name] = {
                    'type': self._process_foreign_keys(column_name)
                }
            else:
                self.schema[column_name] = {'type': self.orm_mapping.get(column_value)}
        self._delete_extra_columns(extra_columns)

    def _process_foreign_keys(self, column_name):
        if self.orm is SupportedORMs.DjangoORM:
            if not self.follow_nested:
                return self.orm_mapping.get(
                    self.model._meta.get_field(column_name).target_field.model._meta.local_fields[0].get_internal_type())
            else:
                return {
                    'properties': self.__class__(
                        model=self.model._meta.get_field(column_name).target_field.model,
                        orm=self.orm,
                    ).load(),
                }

    def _delete_extra_columns(self, columns_to_delete):
        for column in columns_to_delete:
            self.schema.pop(column)

    def _get_model_columns(self):
        columns = {}
        if self.orm is SupportedORMs.SQLAlchemy:
            for column in self.model.__table__.columns:
                columns[column.name] = column.type.__class__.__visit_name__
        if self.orm is SupportedORMs.Peewee:
            for column_name, column_meta in self.model._meta.columns.items():
                columns[column_name] = column_meta.__class__.field_type
        if self.orm is SupportedORMs.DjangoORM:
            for column_name in self.model._meta.local_fields:
                columns[column_name.__dict__['name']] = column_name.get_internal_type()
        return columns

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
