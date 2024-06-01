import pytest

from user.models import Person, Task


@pytest.mark.django_db
def test_person(admin_person):
    assert isinstance(admin_person, Person)
    assert (
        str(admin_person)
        == admin_person.name 
    )


@pytest.mark.django_db
def test_task(task):
    assert isinstance(task, Task)
    assert (
        str(task)
        == task.title 
    )
