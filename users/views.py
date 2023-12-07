from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.shortcuts import render, HttpResponseRedirect, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import auth, messages
from django.urls import reverse, reverse_lazy
from django.utils.http import urlsafe_base64_decode
from django.views.generic import TemplateView, View
from django.contrib.auth.tokens import default_token_generator as token_generator

from products.models import Basket
from users.utils import send_mail_for_verify
from users.forms import Userloginform, UserRegistrationform, Userprofileform


class UserLoginView(View):
    def post(self, request):
        form = Userloginform(data=request.POST)
        if form.is_valid():
            username = request.POST['username']
            password = request.POST['password']
            user = auth.authenticate(username=username, password=password)
            if user and user.email_verify:
                auth.login(request, user)
                return HttpResponseRedirect(reverse('index'))
            elif not user.email_verify:
                messages = ['Ваш email не подтвержден, мы отправили вам новую ссылку для подтверждения '
                            'электронной почты']
                user = auth.authenticate(username=username, password=password)
                send_mail_for_verify(request, user)
            else:
                messages = ['Неправильный логин или пароль']
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
            send_mail_for_verify(request, user)
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
        return redirect('invalid_verify')

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
        else:
            print(form.errors)

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


def logout(request):
    auth.logout(request)
    return HttpResponseRedirect(reverse_lazy('index'))
