import random

from django.contrib.auth import get_user_model
from django.conf import settings
from django.core.mail import EmailMessage
from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    email_verify = models.BooleanField(default=False)
    image = models.ImageField(upload_to='users_images', null=True, blank=True)


