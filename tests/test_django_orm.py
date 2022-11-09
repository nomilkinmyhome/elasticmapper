import os

import pytest
from django.conf import settings
from django.apps import apps
from django.db import models

from elasticmapper import load, SupportedORMs

conf = {
    'INSTALLED_APPS': ['tests'],
    'DATABASES': {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join('.', 'db.sqlite3'),
        }
    }
}
settings.configure(**conf)
apps.populate(settings.INSTALLED_APPS)


class User(models.Model):
    username = models.CharField(max_length=30)
    is_active = models.BooleanField(default=True)
    age = models.SmallIntegerField()


class Post(models.Model):
    title = models.CharField(max_length=200)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')


def test_django_mapping():
    user_elastic_mapping = load(
        model=User,
        orm=SupportedORMs.DjangoORM,
        include=('username', 'age'),
    )
    assert user_elastic_mapping['username'] == {'type': 'text'}
    assert user_elastic_mapping['age'] == {'type': 'short'}
    assert 'is_active' not in user_elastic_mapping
    assert 'id' not in user_elastic_mapping


@pytest.mark.parametrize(
    'follow_nested, excepted_result',
    [
        (False, {'type': 'integer'}),
        (True, {'type': {
            'properties': {
                'id': {'type': 'integer'},
                'username': {'type': 'text'},
                'is_active': {'type': 'boolean'},
                'age': {'type': 'short'},
            },
        }}),
    ]
)
def test_django_fk_mapping(follow_nested, excepted_result):
    post_elastic_mapping = load(
        model=Post,
        orm=SupportedORMs.DjangoORM,
        follow_nested=follow_nested,
    )
    assert post_elastic_mapping['author'] == excepted_result
