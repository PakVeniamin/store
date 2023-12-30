from django.conf import settings
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator as token_generator

from celery_app import app
from users.models import User


@app.task
def send_mail_for_verify(user_id):
    user = User.objects.get(id=user_id)
    context = {
        'user_pk': user_id,
        'user_email': user.email,
        'domain': settings.DOMAIN,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': token_generator.make_token(user),
    }
    message = render_to_string(
        'users/EmailVerification/vetify_email.html',
        context,
    )
    email = EmailMessage(
        'Верификация почтового ящика',
        message,
        from_email=settings.EMAIL_HOST_USER,
        to=[user.email],
    )
    email.send()
