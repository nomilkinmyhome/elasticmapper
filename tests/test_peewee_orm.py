from peewee import *

from elasticmapper import load, SupportedORMs

db = SqliteDatabase('my_app.db')


class BaseModel(Model):
    class Meta:
        database = db


class User(BaseModel):
    username = CharField(unique=True)
    is_active = BooleanField(default=True)
    age = SmallIntegerField()
    name_keyword = CharField()


def test_peewee_mapping():
    user_elastic_mapping = load(
        model=User,
        orm=SupportedORMs.Peewee,
        keyword_fields=['name_keyword'],
    )
    assert user_elastic_mapping['id'] == {'type': 'integer'}
    assert user_elastic_mapping['username'] == {'type': 'text'}
    assert user_elastic_mapping['age'] == {'type': 'short'}
    assert user_elastic_mapping['is_active'] == {'type': 'boolean'}
    assert user_elastic_mapping['name_keyword'] == {'type': 'keyword'}
