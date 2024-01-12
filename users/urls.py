from django.conf import settings
from django.contrib.auth.views import PasswordResetView, PasswordResetConfirmView, PasswordResetCompleteView
from django.urls import path, reverse_lazy
from django.views.generic import TemplateView
from users.views import UserLoginView, RegistrationView, ProfileView, logout, EmailVerify, \
    UserForgotPasswordView, UserPasswordResetConfirmView

app_name = 'users'

urlpatterns = [
    path('login/', UserLoginView.as_view(), name='login'),
    path('register/', RegistrationView.as_view(), name='registration'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('logout/', logout, name='logout'),
    path('invalid_verify/', TemplateView.as_view(template_name='users/EmailVerification/invalid_verify.html'),
         name='invalid_verify'),
    path('confirm_email/', TemplateView.as_view(template_name='users/EmailVerification/confirm_email.html'),
         name='confirm_email'),
    path('verify/<uidb64>/<token>/', EmailVerify.as_view(), name='verify_email'),
    path('password-reset/', UserForgotPasswordView.as_view(), name='password_reset'),
    path('set-new-password/<uidb64>/<token>/', UserPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
]
