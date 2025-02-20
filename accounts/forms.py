from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.core.validators import MinLengthValidator
from django.forms.utils import ErrorList
from django.utils.safestring import mark_safe

from .models import CustomUser
from django import forms
from django.contrib.auth.forms import AuthenticationForm

class CustomErrorList(ErrorList):
    def __str__(self):
        if not self:
            return ''
        return mark_safe(''.join([
            f'<div class="alert alert-danger" role="alert">{e}</div>' for e in self]))


class CustomUserCreationForm(UserCreationForm):

    email = forms.EmailField(required=True)

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = UserCreationForm.Meta.fields + ('email',)
        error_class = None

    def __init__(self, *args, **kwargs):
        super(CustomUserCreationForm, self).__init__ (*args, **kwargs)
        for fieldname in ['username', 'password', 'password2', 'email']:
            if fieldname in self.fields:
                self.fields[fieldname].help_text = None
                self.fields[fieldname].widget.attrs.update(
                    {'class': 'form-control'}
                )

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            pass
        return email

class SecurityQuestionForm(forms.Form):
    answer1 = forms.CharField(label="Answer to Question 1")
    answer2 = forms.CharField(label="Answer to Question 2")



class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(label="Username")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for fieldname in ['username', 'password']:
            self.fields[fieldname].widget.attrs.update({'class': 'form-control'})


class PasswordResetForm(forms.Form):
    password = forms.CharField(
        widget=forms.PasswordInput,
        label="New Password",
        validators=[MinLengthValidator(8)],
        help_text="Password must be at least 8 characters long."
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput,
        label="Confirm New Password"
    )

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")
        return cleaned_data