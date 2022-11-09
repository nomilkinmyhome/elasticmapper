# ElasticMapper
### ElasticSearch mapper for three ORMs - SQLAlchemy, Peewee, DjangoORM.
#### Allows you to easily generate ElasticSearch mappings based on models.

## Installation

```pip install elasticmapper```

## Basic usage
### Peewee example
```python
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
```

### SQLAlchemy example

```python
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
```

### DjangoORM example

```python
from django.db import models
from elasticmapper import DjangoMapper

class User(models.Model):
    username = models.CharField(max_length=30)
    is_active = models.BooleanField(default=True)
    age = models.IntegerField()

user_elastic_mapping = DjangoMapper(model=User).load()
```

#### Output for all examples: 

```python
{
    'id': {'type': 'integer'},
    'username': {'type': 'text'},
    'age': {'type': 'integer'},
    'is_active': {'type': 'boolean'}
}
```

## Documentation

Documentation lives [here](https://elasticmapper.readthedocs.io/en/latest/).

## Contributing

PR are welcome! If you want to help, please check [the issues](https://github.com/nomilkinmyhome/elasticmapper/issues) and fix one of them. Thank you for your contribution.

## License 

Copyright © 2022 Polina Beskorovaynaya [ihatemilk](https://github.com/nomilkinmyhome)

This project has [MIT License](https://github.com/nomilkinmyhome/elasticmapper/blob/main/LICENSE).
