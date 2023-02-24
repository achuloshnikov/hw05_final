from django.contrib.auth import views
from django.urls import path

from users.views import SignUp

app_name = 'users'

urlpatterns = [
    path('signup/', SignUp.as_view(), name='signup'),
    path(
        'logout/',
        views.LogoutView.as_view(template_name='users/logged_out.html'),
        name='logout',
    ),
    path(
        'login/',
        views.LoginView.as_view(template_name='users/login.html'),
        name='login',
    ),
    path(
        'password_reset_form/',
        views.PasswordResetView.as_view(
            template_name='users/password_reset_form.html',
        ),
        name='password_reset_form',
    ),
    path(
        'password_change_form/',
        views.PasswordChangeView.as_view(
            template_name='users/password_change_form.html',
        ),
        name='password_change_form',
    ),
]
