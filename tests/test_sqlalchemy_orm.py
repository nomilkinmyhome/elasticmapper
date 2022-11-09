from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, Boolean, SmallInteger

from elasticmapper import Mapper, SupportedORMs

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String)
    is_active = Column(Boolean)
    age = Column(SmallInteger)


def test_sqlalchemy_mapping():
    user_elastic_mapping = Mapper(
        model=User,
        orm=SupportedORMs.SQLAlchemy,
        alternative_names={
            'age': 'user_age',
        },
        exclude=['is_active'],
    ).load()
    assert user_elastic_mapping['id'] == {'type': 'integer'}
    assert user_elastic_mapping['username'] == {'type': 'text'}
    assert user_elastic_mapping['user_age'] == {'type': 'short'}
    assert 'is_active' not in user_elastic_mapping
    assert 'age' not in user_elastic_mapping
