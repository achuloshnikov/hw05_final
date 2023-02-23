from django.contrib.auth.views import PasswordChangeView, PasswordResetView
from django.urls import reverse_lazy
from django.views.generic import CreateView

from users.forms import CreationForm, PasswordChange, PasswordReset


class SignUp(CreateView):
    form_class = CreationForm
    success_url = reverse_lazy('posts:index')
    template_name = 'users/signup.html'


class ResetPassword(PasswordResetView):
    form_class = PasswordReset
    success_url = reverse_lazy('posts:index')
    template_name = 'users/password_reset_form.html'


class ChangePassword(PasswordChangeView):
    form_class = PasswordChange
    success_url = reverse_lazy('posts:index')
    template_name = 'users/password_change_form.html'
