from django.contrib.auth.forms import (
    UserCreationForm,
    PasswordResetForm,
    PasswordChangeForm,
)
from django.contrib.auth import get_user_model


User = get_user_model()


class CreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('first_name', 'last_name', 'username', 'email')


class PasswordReset(PasswordResetForm):
    class Meta:
        model = User
        fields = 'email'


class PasswordChange(PasswordChangeForm):
    class Meta:
        model = User
        fields = ('old_password', 'new_password', 'repeat_new_password')
