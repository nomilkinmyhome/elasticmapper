from typing import Collection, Dict, Optional

from elasticmapper.supported_orms import SupportedORMs
from elasticmapper.orm_mappings import (
    sqlalchemy_mapping,
    peewee_mapping,
    django_mapping,
)

_supported_orms = tuple(SupportedORMs)
_orm_fields_mapping = {
    SupportedORMs.SQLAlchemy: sqlalchemy_mapping,
    SupportedORMs.Peewee: peewee_mapping,
    SupportedORMs.DjangoORM: django_mapping,
}


def load(
        model,
        orm: Optional[SupportedORMs],
        keyword_fields: Optional[Collection[str]] = None,
        alternative_names: Optional[Dict[str, str]] = None,
        include: Collection[Optional[str]] = (),
        exclude: Collection[Optional[str]] = (),
):
    if orm not in _supported_orms:
        raise RuntimeError(f'ORM is not supported yet. '
                           f'Supported ORMs: {[value for _, value in _supported_orms]}')

    orm_mapping = _orm_fields_mapping.get(orm)
    schema = _get_model_columns(model, orm)
    _fill_schema(schema, exclude, include, orm_mapping)

    if keyword_fields is not None:
        _fill_keyword_fields(schema, keyword_fields)

    if alternative_names is not None:
        schema = _rename_fields_using_alternative_names(
            schema,
            alternative_names,
        )

    return schema


def _fill_schema(schema, exclude, include, orm_mapping):
    extra_columns = []
    for column_name, column_value in schema.items():
        conditions = (
            (exclude and column_name in exclude),
            (include and column_name not in include),
        )
        if any(conditions):
            extra_columns.append(column_name)
        schema[column_name] = {'type': orm_mapping.get(column_value)}
    _delete_extra_columns(schema, extra_columns)


def _delete_extra_columns(schema, columns_to_delete):
    for column in columns_to_delete:
        schema.pop(column)


def _get_model_columns(model, orm):
    columns = {}
    if orm is SupportedORMs.SQLAlchemy:
        for column in model.__table__.columns:
            columns[column.name] = column.type.__class__.__visit_name__
    if orm is SupportedORMs.Peewee:
        for column_name, column_meta in model._meta.columns.items():
            columns[column_name] = column_meta.__class__.field_type
    if orm is SupportedORMs.DjangoORM:
        for column_name in model._meta.local_fields:
            columns[column_name.__dict__['name']] = column_name.get_internal_type()
    return columns


def _fill_keyword_fields(schema, keyword_fields):
    for column_name in schema.keys():
        if column_name in keyword_fields:
            schema[column_name] = {'type': 'keyword'}


def _rename_fields_using_alternative_names(schema, alternative_names):
    new_schema = schema.copy()
    for column_name, column_type in schema.items():
        for old_name, new_name in alternative_names.items():
            if column_name == old_name:
                new_schema[new_name] = {'type': column_type['type']}
                new_schema.pop(old_name)
    return new_schema
