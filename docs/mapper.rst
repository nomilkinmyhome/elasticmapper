Mapper
====================

Mapper - base class for all ORM mappers.

You have to use one of them: ``DjangoMapper``, ``SQLAlchemyMapper``, ``PeeweeMapper``.

============
``elasticmapper.Mapper`` params
============

**model**

A model instance.

**keyword_fields**

A collection that contains attribute names. All of them will have ```keyword``` type in the output mapping.

**include**

A collection that contains attribute names. Attributes that are not listed in this collection will not be included in the output mapping.

**exclude**

A collection that contains attribute names. Attributes that are listed in this collection will not be included in the output mapping.

**alternative_names**

A dictionary that contains attribute names and their new names which will be listed in the output mapping.

For example:

``DjangoMapper(model=..., alternative_names={'id': 'obj_id'}).load()``

Expected output:

``{'obj_id': 'int'}``

**follow_nested**

When it is False, generated mapping with FK contains only type of the relation field, otherwise mapping contains related model schema.
