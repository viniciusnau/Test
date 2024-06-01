import json
from django.test import Client
import pytest
from user.models import Person, Task


@pytest.mark.django_db
def test_task_retrieve_update_destroy_view(task, super_user):
    client = Client()
    client.force_login(super_user)
    response = client.get(f'/task/{task.id}/')
    assert response.status_code == 404
