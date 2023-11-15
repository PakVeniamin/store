import random

from django.contrib.auth import get_user_model
from django.conf import settings
from django.core.mail import EmailMessage
from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    is_active = models.BooleanField(default=False)
    image = models.ImageField(upload_to='users_images', null=True, blank=True)


class VerificationCode(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.user.email}: {self.code}'

    def generate_code(self):
        self.code = "".join(random.choices("0123456789", k=6))
        self.save()

    def send_code(self):
        subject = 'Код подтверждения'
        message = f'Здравствуйте {self.user.username} Ваш код подтверждения регистрации: {self.code}'
        from_email = settings.EMAIL_HOST_USER
        to_email = [self.user.email]
        email = EmailMessage(subject, message, from_email, to_email)
        email.send()
        print('Код успешно отправлен')
