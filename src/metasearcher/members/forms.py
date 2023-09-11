from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django import forms
from django.contrib.auth.models import User
from crispy_bootstrap5.bootstrap5 import FloatingField

from crispy_forms.helper import FormHelper, Layout
from crispy_forms.layout import Row, Column, Div, BaseInput

class CustomUserForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=50, required=True)
    last_name = forms.CharField(max_length=50, required=True)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']

    helper = FormHelper()
    helper.form_tag = False
    helper.disable_csrf = True

class CustomAuthenticationForm(AuthenticationForm):
    helper = FormHelper()
    helper.form_tag = False
    helper.disable_csrf = True
    helper.layout = Layout(
        Div(
            FloatingField('username', wrapper_class="login_class")
        ),
        Div(
            FloatingField('password')
        )
    )