from elasticmapper.orm_mappings.sqlalchemy_mapping import mapping as sqlalchemy_mapping
from elasticmapper.orm_mappings.peewee_mapping import mapping as peewee_mapping
from elasticmapper.orm_mappings.django_mapping import mapping as django_mapping

__all__ = (
    sqlalchemy_mapping,
    peewee_mapping,
    django_mapping,
)
