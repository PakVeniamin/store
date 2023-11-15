
from django.shortcuts import render, HttpResponseRedirect, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import auth, messages
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import FormView, TemplateView, View
from products.models import Basket
from users.models import VerificationCode

from users.forms import Userloginform, UserRegistrationform, Userprofileform


class UserLoginView(View):
    def post(self, request):
        form = Userloginform(data=request.POST)
        if form.is_valid():
            username = request.POST['username']
            password = request.POST['password']
            user = auth.authenticate(username=username, password=password)
            if user:
                auth.login(request, user)
                return HttpResponseRedirect(reverse('users:verify'))
        context = {'form': form}
        return render(request, 'users/login.html', context)

    def get(self, request):
        form = Userloginform()
        context = {'form': form}
        return render(request, 'users/login.html', context)


class RegistrationView(FormView):
    form_class = UserRegistrationform
    template_name = 'users/register.html'
    success_url = reverse_lazy('users:verify')

    def form_valid(self, form):
        user = form.save()
        verification_code = VerificationCode(user=user)
        verification_code.generate_code()
        verification_code.send_code()
        messages.success(self.request, 'Вы успешно зарегистрировались! '
                                       'Пожалуйста, проверьте свою почту и введите код подтверждения')
        auth.login(self.request, user)
        return super().form_valid(form)


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


class VerifyView(View):
    def get(self, request):
        user = request.user
        if user.is_authenticated:
            try:
                verification_code = VerificationCode.objects.get(user=user)
            except VerificationCode.DoesNotExist:
                verification_code = VerificationCode(user=user)
                verification_code.generate_code()
                verification_code.send_code()
            return render(request, 'users/verify.html')
        else:
            return redirect('users:login')

    def post(self, request):
        user = request.user
        input_code = request.POST.get('code')
        try:
            verification_code = VerificationCode.objects.get(user=user)
        except VerificationCode.DoesNotExist:
            messages.error(request, 'У вас нет кода подтверждения, пожалуйста, запросите новый')
            return redirect('users:verify')

        if input_code == verification_code.code:
            user.is_active = True
            user.save()
            verification_code.delete()
            messages.success(request, 'Ваша учетная запись активирована'
                                      'Теперь вы можете зайти на сайт')
            return redirect('users:login')
        else:
            return render(request, 'users/verify.html', {'error': 'Неправильный код подтверждения'})

def logout(request):
    auth.logout(request)
    return HttpResponseRedirect(next_page=reverse_lazy('index'))
