import random
import smtplib

from django.conf import settings
from email.message import EmailMessage
from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    image = models.ImageField(upload_to='users_images', null=True, blank=True)


class VerificationCode(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.user.username}: {self.code}'

    def generate_code(self):
        self.code = "".join(random.choices("023456789", k=6))
        self.save()

    def send_code(self):
        msg = EmailMessage()
        msg['Subject'] = 'Успешная регистрация'
        msg['From'] = settings.EMAIL_HOST_USER
        msg['To'] = self.user.email
        msg.set_content(f'Здравствуйте, {self.user.username}! Ваш код подтверждения: {self.code}')

        with smtplib.SMTP_SSL(settings.EMAIL_HOST, settings.EMAIL_PORT) as server:
            server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
            server.send_message(msg)
            print("Код успешно отправлен")


