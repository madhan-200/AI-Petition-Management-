from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    class Roles(models.TextChoices):
        CITIZEN = 'CITIZEN', 'Citizen'
        OFFICER = 'OFFICER', 'Officer'
        ADMIN = 'ADMIN', 'Admin'

    role = models.CharField(max_length=20, choices=Roles.choices, default=Roles.CITIZEN)
    department = models.ForeignKey(
        'petitions.Department', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        help_text="Department for officers"
    )
    is_active_officer = models.BooleanField(
        default=True, 
        help_text="Whether officer is available for assignments"
    )
