from django.contrib.auth.forms import (UserCreationForm,
                                       PasswordChangeForm,
                                       PasswordResetForm,
                                       SetPasswordForm)
from django.contrib.auth import get_user_model


User = get_user_model()


class CreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('first_name', 'last_name', 'username', 'email')


class PasswordChangingForm(PasswordChangeForm):
    class Meta:
        model = User
        fields = ('old_password', 'password1', 'password2')


class PasswordResettingForm(PasswordResetForm):
    class Meta:
        model = User
        fields = ('email',)


class SettingPasswordForm(SetPasswordForm):
    class Meta:
        model = User
        fields = ('password1', 'password2')
