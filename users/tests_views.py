from django.test import TestCase, Client
from users.views import UserLoginView
from users.forms import Userloginform
from django.urls import reverse
from users.models import User

class UserLoginViewTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='Nikita', password='qwertyasdfgh123546',
                                             email='Nikita@mail.ru')
        self.user.email_verify = True
        self.user.save()
        self.client = Client()

    def test_login_success(self):
        response = self.client.post(reverse('users:login'),
                                    {'username': 'Nikita', 'password': 'qwertyasdfgh123546'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('index'))
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_wrong_login_or_password(self):
        response = self.client.post(reverse('users:login'), {'username': 'Nikita', 'password': 'qwerytasdfgj123456'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['messages'], ['Неправильный логин или пароль'])
        self.assertFalse(response.wsgi_request.user.is_authenticated)


    def test_login_fail_unverified_email(self):
        self.user.email_verify = False
        self.user.save()
        response = self.client.post(reverse('users:login'), {'username': 'Nikita', 'password': 'qwertyasdfgh123546'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['messages'], ['Ваш email не подтвержден, мы отправили вам '
                                                        'новую ссылку для подтверждения электронной почты'])
        self.assertFalse(response.wsgi_request.user.is_authenticated)

    def test_login_get(self):
        # отправляем GET-запрос
        response = self.client.get(reverse('users:login'))
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context['form'], Userloginform)