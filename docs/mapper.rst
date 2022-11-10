Mapper
====================

Mapper - base class for all ORM mappers.

You have to use one of them: ``DjangoMapper``, ``SQLAlchemyMapper``, ``PeeweeMapper``.

============
``elasticmapper.Mapper`` params
============

^^^^
model ``: Union[django.models.Model, peewee.Model, sqlalchemy.declarative_base()]``
^^^^

A model instance.

^^^^
keyword_fields ``: Iterable[str]``
^^^^

Contains attribute names. All of them has ``keyword`` type in the output mapping.

^^^^
include ``: Iterable[str]``
^^^^

Contains attribute names. Result mapping contains only these attributes, the others will not be included.

^^^^
exclude ``: Iterable[str]``
^^^^

Contains attribute names. Result mapping contains all attributes except for them.

^^^^
alternative_names ``: Dict[str, str]``
^^^^

Contains attribute names and their new names. Result mapping has only new names instead of originals.

For example:

``DjangoMapper(model=..., alternative_names={'id': 'obj_id'}).load()``

Expected output:

``{'obj_id': 'integer'}``

^^^^
follow_nested
^^^^

When it is False, generated mapping with FK contains type of the relation field, otherwise mapping contains related model schema.

For example, ``follow_nested=False``:

.. code-block:: python

    mapping = DjangoMapper(
        model=SomeModel,
        follow_nested=False,
    ).load()

Output:

.. code-block:: json

    {"type": "integer"}

Because foreign model has ``Integer`` PK-field

``follow_nested=True`` generates this mapping:

.. code-block:: json

    {"type": {
        "properties": {
            "id": {"type": "integer"},
            "username": {"type": "text"},
            "is_active": {"type": "boolean"},
            "age": {"type": "short"},
        },
    }}

Now we see foreign model schema instead of PK-field's type
