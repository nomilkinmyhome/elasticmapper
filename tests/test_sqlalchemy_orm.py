import pytest

from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy import Column, Integer, String, Boolean, SmallInteger, ForeignKey

from elasticmapper import SQLAlchemyMapper
from tests.common import fk_mapping_test_data

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String)
    is_active = Column(Boolean)
    age = Column(SmallInteger)
    posts = relationship('Post')


class Post(Base):
    __tablename__ = 'posts'

    id = Column(Integer, primary_key=True)
    title = Column(String)
    author = Column(Integer, ForeignKey('users.id'))


def test_sqlalchemy_mapping():
    user_elastic_mapping = SQLAlchemyMapper(
        model=User,
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


@pytest.mark.parametrize(
    'follow_nested, excepted_result',
    fk_mapping_test_data,
)
def test_sqlalchemy_fk_mapping(follow_nested, excepted_result):
    post_elastic_mapping = SQLAlchemyMapper(
        model=Post,
        follow_nested=follow_nested,
    ).load()
    assert post_elastic_mapping['author'] == excepted_result
