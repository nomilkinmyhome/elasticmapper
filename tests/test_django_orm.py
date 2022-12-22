import os
import uuid

import pytest
from django.conf import settings
from django.apps import apps
from django.db import models

from elasticmapper import DjangoMapper
from tests.common import fk_mapping_test_data

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
    json_data = models.JSONField(default=dict())


class Post(models.Model):
    title = models.CharField(max_length=200)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')


class Tag(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    title = models.CharField(max_length=30)
    score = models.FloatField(default=3.0)
    # posts = models.ManyToManyField(to=Post)


def test_django_mapping():
    custom_values = {
        'json_data': {
            'type': {
                'properties': {
                    'key': {'type': 'integer'},
                },
            },
        },
    }
    user_elastic_mapping = DjangoMapper(
        model=User,
        include=('username', 'age'),
        custom_values=custom_values,
    ).load()
    assert user_elastic_mapping['username'] == {'type': 'text'}
    assert user_elastic_mapping['age'] == {'type': 'short'}
    assert user_elastic_mapping['json_data'] == custom_values['json_data']
    assert 'is_active' not in user_elastic_mapping
    assert 'id' not in user_elastic_mapping


@pytest.mark.parametrize(
    'follow_nested, excepted_result',
    fk_mapping_test_data,
)
def test_django_fk_mapping(follow_nested, excepted_result):
    post_elastic_mapping = DjangoMapper(
        model=Post,
        follow_nested=follow_nested,
    ).load()
    for item in excepted_result:
        assert item in post_elastic_mapping['author']


@pytest.mark.skip("no m2m support")
def test_m2m():
    mapping = DjangoMapper(model=Tag).load()
    assert mapping['id'] == {'type': 'text'}
    assert mapping['title'] == {'type': 'text'}
    assert mapping['score'] == {'type': 'float'}
    assert mapping['posts'] == {'type': 'float'}
