from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model


class EmailBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        user_model = get_user_model()
        try:
            user = user_model.objects.get(username=username)
            if user.check_password(password) and user.is_active:
                return user
        except user_model.DoesNotExists:
            return None
