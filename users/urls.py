from django.conf import settings
from django.contrib.auth.views import PasswordResetView, PasswordResetConfirmView, PasswordResetCompleteView
from django.urls import path, reverse_lazy
from django.views.generic import TemplateView
from users.views import UserLoginView, RegistrationView, ProfileView, logout, EmailVerify

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
    path('password-reset/done/',
         PasswordResetView.as_view(template_name='users/ResetPassword/password_reset_letter.html'),
         name='password_reset_done'),
    path('password-reset/',
         PasswordResetView.as_view(template_name='users/ResetPassword/password_reset_form.html',
                                   from_email=settings.EMAIL_HOST_USER,
                                   extra_email_context={'expiry_times': 15},
                                   email_template_name='users/ResetPassword/password_reset_email.html',
                                   html_email_template_name='users/ResetPassword/password_reset_email.html',
                                   success_url=reverse_lazy('users:password_reset_done')),
         name='password_reset'),
    path('password-reset/<uidb64>/<token>/',
         PasswordResetConfirmView.as_view(template_name='users/ResetPassword/password_reset_confirm.html',
                                          success_url=reverse_lazy('users:password_reset_complete')),
         name='password_reset_confirm'),
    path('password-reset/complete/',
         PasswordResetCompleteView.as_view(template_name="users/ResetPassword/password_reset_complete.html"),
         name='password_reset_complete'),

]
