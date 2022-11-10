Basic usage
====================

------------
Peewee example
------------

.. code-block:: python

    from peewee import *
    from elasticmapper import PeeweeMapper

    db = SqliteDatabase('my_app.db')

    class BaseModel(Model):
        class Meta:
            database = db

    class User(BaseModel):
        username = CharField(unique=True)
        is_active = BooleanField(default=True)
        age = IntegerField()

    user_elastic_mapping = PeeweeMapper(model=User).load()


------------
SQLAlchemy example
------------

.. code-block:: python

    from sqlalchemy.orm import declarative_base
    from sqlalchemy import Column, Integer, String, Boolean
    from elasticmapper import SQLAlchemyMapper

    Base = declarative_base()

    class User(Base):
        __tablename__ = 'users'
        id = Column(Integer, primary_key=True)
        username = Column(String)
        is_active = Column(Boolean)
        age = Column(Integer)

    user_elastic_mapping = SQLAlchemyMapper(model=User).load()


------------
DjangoORM example
------------

.. code-block:: python

    from django.db import models
    from elasticmapper import DjangoMapper

    class User(models.Model):
        username = models.CharField(max_length=30)
        is_active = models.BooleanField(default=True)
        age = models.IntegerField()

    user_elastic_mapping = DjangoMapper(model=User).load()


**Output for all examples**

.. code-block:: json

    {
        "id": {"type": "integer"},
        "username": {"type": "text"},
        "age": {"type": "integer"},
        "is_active": {"type": "boolean"}
    }
