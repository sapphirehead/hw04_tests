from django.views.generic import CreateView
from django.urls import reverse_lazy
from .forms import CreationForm
from django.contrib.auth.views import (PasswordChangeView,
                                       PasswordResetView,
                                       PasswordResetConfirmView)
from .forms import (PasswordChangingForm,
                    PasswordResettingForm,
                    SettingPasswordForm)


class SignUp(CreateView):
    form_class = CreationForm
    success_url = reverse_lazy('posts:index')
    template_name = 'users/signup.html'


class PasswordChangingView(PasswordChangeView):
    form_class = PasswordChangingForm
    success_url = reverse_lazy('users:password_change_done')
    template_name = 'users/password_change_form.html'


class PasswordResettingView(PasswordResetView):
    form_class = PasswordResettingForm
    success_url = reverse_lazy('users:password_reset_done')
    template_name = 'users/password_reset_form.html'


class PasswordResettingConfirmView(PasswordResetConfirmView):
    form_class = SettingPasswordForm
    success_url = reverse_lazy('users:password_reset_complete')
    template_name = 'users/password_reset_confirm.html'
