from django.contrib.auth import get_user_model
from django.contrib.auth.forms import SetPasswordForm, PasswordResetForm
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import ValidationError
from django.shortcuts import render, HttpResponseRedirect, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import auth
from django.urls import reverse, reverse_lazy
from django.utils.http import urlsafe_base64_decode
from django.views.generic import TemplateView, View
from django.contrib.auth.tokens import default_token_generator as token_generator
from django.contrib.auth.views import PasswordResetView, PasswordResetConfirmView

from products.models import Basket
from users.email import send_mail_for_verify
from users.forms import Userloginform, UserRegistrationform, Userprofileform


class UserLoginView(View):
    def post(self, request):
        form = Userloginform(data=request.POST)
        messages = []
        if form.is_valid():
            username = request.POST['username']
            password = request.POST['password']
            user = auth.authenticate(username=username, password=password)

            if user is not None and user.email_verify:
                auth.login(request, user)
                return HttpResponseRedirect(reverse('index'))
            elif user is not None and not user.email_verify:
                messages.append('Ваш email не подтвержден, мы отправили вам новую ссылку для подтверждения '
                                'электронной почты')
                send_mail_for_verify.delay(user.id, request.META['HTTP_HOST'])

            else:
                messages.append('Неправильный логин или пароль')
        context = {'form': form, 'messages': messages}
        return render(request, 'users/login.html', context)

    def get(self, request):
        form = Userloginform()
        context = {'form': form}
        return render(request, 'users/login.html', context)


class RegistrationView(View):
    form_class = UserRegistrationform
    template_name = 'users/register.html'

    def get(self, request):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = auth.authenticate(username=username, password=password)
            send_mail_for_verify.delay(user.id, request.META['HTTP_HOST'])
            return redirect('users:confirm_email')
        context = {
            'form': form
        }
        return render(request, self.template_name, context)


User = get_user_model()


class EmailVerify(View):
    def get(self, request, uidb64, token):
        user = self.get_user(uidb64)

        if user is not None and token_generator.check_token(user, token):
            user.email_verify = True
            user.save()
            auth.login(request, user)
            return redirect('users:login')
        return redirect('users:invalid_verify')

    @staticmethod
    def get_user(uidb64):
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError,
                User.DoesNotExist, ValidationError):
            user = None
        return user


class ProfileView(LoginRequiredMixin, TemplateView):
    def post(self, request):
        form = Userprofileform(instance=request.user, data=request.POST, files=request.FILES)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('users:profile'))

        context = self.get_context_data(form=form)
        return render(request, 'users/profile.html', context)

    def get(self, request):
        form = Userprofileform(instance=request.user)
        context = self.get_context_data(form=form)
        return render(request, 'users/profile.html', context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Store-Профиль'
        context['baskets'] = Basket.objects.filter(user=self.request.user)
        return context


class UserForgotPasswordView(SuccessMessageMixin, PasswordResetView):
    """
    Представление по сбросу пароля по почте
    """
    form_class = PasswordResetForm
    template_name = 'users/ResetPassword/user_password_reset.html'
    success_url = reverse_lazy('users:login')
    success_message = 'Письмо с инструкцией по восстановлению пароля отправлена на ваш email'
    email_template_name = 'users/ResetPassword/password_reset_mail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Запрос на восстановление пароля'
        return context


class UserPasswordResetConfirmView(SuccessMessageMixin, PasswordResetConfirmView):
    """
    Представление установки нового пароля
    """
    form_class = SetPasswordForm
    template_name = 'users/ResetPassword/user_password_set_new.html'
    success_url = reverse_lazy('users:login')
    success_message = 'Пароль успешно изменен. Можете авторизоваться на сайте.'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Установить новый пароль'
        return context


def logout(request):
    auth.logout(request)
    return HttpResponseRedirect(reverse_lazy('index'))
