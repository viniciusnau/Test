from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class Person(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    # is_resident = models.BooleanField(default=False)
    name = models.CharField("Name", max_length=255, default="")
    birth_date = models.DateField("Birth Date", blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name
