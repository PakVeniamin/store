from django.shortcuts import render, HttpResponseRedirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import auth, messages
from django.urls import reverse, reverse_lazy
from django.views.generic import FormView, TemplateView, View
from products.models import Basket

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
                return HttpResponseRedirect(reverse('index'))
        context = {'form': form}
        return render(request, 'users/login.html', context)

    def get(self, request):
        form = Userloginform()
        context = {'form': form}
        return render(request, 'users/login.html', context)


class RegistrationView(FormView):
    form_class = UserRegistrationform
    template_name = 'users/register.html'
    success_url = reverse_lazy('users:login')

    def form_valid(self, form):
        form.save()
        messages.success(self.request, 'Ты справился с регистрацией!')
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


def logout(request):
    auth.logout(request)
    return HttpResponseRedirect(reverse('index'))
