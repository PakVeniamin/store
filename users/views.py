from django.shortcuts import render, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib import auth, messages
from django.urls import reverse, reverse_lazy
from django.views.generic import FormView
from products.models import Basket


from users.forms import Userloginform, UserRegistrationform, Userprofileform


def login(request):
    if request.method == 'POST':
        form = Userloginform(data=request.POST)
        if form.is_valid():
            username = request.POST['username']
            password = request.POST['password']
            user = auth.authenticate(username=username, password=password)
            if user:
                auth.login(request, user)
                return HttpResponseRedirect(reverse('index'))
    else:
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


@login_required
def profile(request):
    if request.method == 'POST':
        form = Userprofileform(instance=request.user, data=request.POST, files=request.FILES)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('users:profile'))
        else:
            print(form.errors)
    else:
        form = Userprofileform(instance=request.user)

    context = {'title': 'Store - Профиль',
               'form': form,
               'baskets': Basket.objects.filter(user=request.user)
               }
    return render(request, 'users/profile.html', context)


def logout(request):
    auth.logout(request)
    return HttpResponseRedirect(reverse('index'))