from enum import Enum


class SupportedORMs(Enum):
    SQLAlchemy = 'SQLAlchemy'
    Peewee = 'Peewee'
    DjangoORM = 'DjangoORM'
