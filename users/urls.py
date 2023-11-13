from django.urls import path

from users.views import UserLoginView, RegistrationView, ProfileView, logout, VerifyView

app_name = 'users'

urlpatterns = [
    path('login/', UserLoginView.as_view(), name='login'),
    path('register/', RegistrationView.as_view(), name='registration'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('logout/', logout, name='logout'),
    path('login/verify/', VerifyView.as_view(), name='verify')
]
