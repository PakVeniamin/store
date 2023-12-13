from django.test import TestCase, Client
from django.core import mail
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator as token_generator

from users.forms import Userloginform, UserRegistrationform
from django.urls import reverse
from users.models import User
from users.views import EmailVerify


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
        self.user.save()
        response = self.client.post(reverse('users:login'), {'username': 'Nikita', 'password': 'qwertyasdfgh123546'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.context['messages'], ['Ваш email не подтвержден, мы отправили вам '
                                                        'новую ссылку для подтверждения электронной почты'])
        self.assertFalse(response.wsgi_request.user.is_authenticated)

    def test_login_get(self):
        # отправляем GET-запрос
        response = self.client.get(reverse('users:login'))
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context['form'], Userloginform)


class RegistrationViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.url = reverse('users:registration')
        self.user_data = {
            'first_name': 'test',
            'last_name': 'test2',
            'username': 'testuser',
            'email': 'testuser@example.ru',
            'password1': 'testpassword',
            'password2': 'testpassword',
        }

    def test_get_registration_view(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/register.html')
        self.assertIsInstance(response.context['form'], UserRegistrationform)

    def test_post_user_registration_view(self):
        response = self.client.post(self.url, self.user_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('users:confirm_email'))
        user = User.objects.get(username=self.user_data['username'])
        self.assertIsNotNone(user)

        self.assertEqual(user.is_authenticated, True)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'Верификация почтового ящика')
        self.assertEqual(mail.outbox[0].to, [self.user_data['email']])
        self.assertIn('http://testserver/users/verify/', mail.outbox[0].body)


class EmailVerifyTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='test123')
        self.user.email_verify = False
        self.user.save()

    def test_get_user(self):
        uidb64 = urlsafe_base64_encode(force_bytes(self.user.pk))
        user = EmailVerify.get_user(uidb64)
        self.assertEqual(user, self.user)

    def test_get_user_invalid(self):
        uidb64 = 'invalid'
        user = EmailVerify.get_user(uidb64)
        self.assertIsNone(user)

    def test_get_valid(self):
        uidb64 = urlsafe_base64_encode(force_bytes(self.user.pk))
        token = token_generator.make_token(self.user)
        response = self.client.get(reverse('users:verify_email', args=[uidb64, token]))
        self.assertRedirects(response, reverse('users:login'))

    def test_get_invalid(self):
        uidb64 = urlsafe_base64_encode(force_bytes(self.user.pk))
        token = 'invalid'
        response = self.client.get(reverse('users:verify_email', args=[uidb64, token]))
        self.assertRedirects(response, reverse('users:invalid_verify'))

    def test_email_verify(self):
        uidb64 = urlsafe_base64_encode(force_bytes(self.user.pk))
        token = token_generator.make_token(self.user)
        self.assertFalse(self.user.email_verify)
        response = self.client.get(reverse('users:verify_email', args=[uidb64, token]))
        self.user.refresh_from_db()
        self.assertTrue(self.user.email_verify)


class ProfileViewTest(TestCase):
    def setUP(self):
        self.user = User.objects.create_user(username='testuser', email='test@example.ru', password='test123')
        self.client = Client()
        self.client.login(username='testuser', password='test123')
        self.test_form_date = {
            'username': 'testuser',
            'password': 'test123',
        }
        self.test_file = {
            'image': '"C:\\Users\\venia\\OneDrive\\Изображения\\u2vVVLvoh-g.jpg"'
        }

    def test_get_profile_view(self):
        response = self.client.get(reverse('users:profile'))
        self.assertEqual(response.status_code, 302)
        self.assertTemplateUsed(response, 'users/profile.html')
        self.assertIn('form', response.context)
        self.assertIn('baskets', response.context)
        self.assertEqual(response.context['title'], 'Store-Профиль')
