from django.views.generic import CreateView
from django.urls import reverse_lazy
from django.contrib.auth.views import PasswordResetView, PasswordChangeView

from users.forms import CreationForm, PasswordReset, PasswordChange


class SignUp(CreateView):
    form_class = CreationForm
    success_url = reverse_lazy('posts:index')
    template_name = 'users/signup.html'


class PasswordReset(PasswordResetView):
    form_class = PasswordReset
    success_url = reverse_lazy('posts:index')
    template_name = 'users/password_reset_form.html'


class PasswordChange(PasswordChangeView):
    form_class = PasswordChange
    success_url = reverse_lazy('posts:index')
    template_name = 'users/password_change_form.html'
