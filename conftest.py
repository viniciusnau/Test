import pytest

from django.contrib.auth.models import User
from datetime import date
from datetime import datetime, timedelta

from user.models import (
    Person,
    Task
)


@pytest.fixture(autouse=True)
def setup_environment_variables(monkeypatch):
    monkeypatch.setenv("AWS_BUCKET_NAME", "test_bucket")
    monkeypatch.setenv("AWS_EXPIRES_SECONDS", "3600")
    monkeypatch.setenv("AWS_REGION_NAME", "eu-north-1")
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "test_access_key")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "test_secret_access_key")
    monkeypatch.setenv("DATABASE_HOST", "test_host"),
    monkeypatch.setenv("DATABASE_PORT", "1234"),
    monkeypatch.setenv("DATABASE_PORT", "1234"),
    monkeypatch.setenv("EMAIL_HOST_USER", "test_host_email@example.com")


@pytest.fixture
def regular_user():
    return User.objects.create_user(
        username="regular_user",
        password="regular_user",
        email="regular_email@example.com",
    )


@pytest.fixture
def extra_regular_user():
    return User.objects.create_user(
        username="regular_user_extra",
        password="regular_user_extra",
        email="regular_email_extra@example.com",
    )


@pytest.fixture
def super_user():
    return User.objects.create_superuser(
        username="admin", email="admin@example.com", password="admin"
    )


@pytest.fixture
def extra_super_user():
    return User.objects.create_superuser(
        username="admin_extra", email="admin_extra@example.com", password="admin_extra"
    )


@pytest.fixture
def admin_person(super_user):
    return Person.objects.create(
        user=super_user,
        name="Test Name"
    )


@pytest.fixture
def person(regular_user):
    return Person.objects.create(
        user=regular_user, name="test_client_user"
    )


@pytest.fixture
def task(person):
    return Task.objects.create(
        person=person, title="test_task"
    )

@pytest.fixture
def extra_person(regular_user_extra):
    return Person.objects.create(
        user=regular_user_extra,
        name="test_client_user_extra",
    )


@pytest.fixture
def extra_admin_person(super_user_extra):
    return Person.objects.create(
        user=super_user_extra,
        name="Test Name Extra",
    )
