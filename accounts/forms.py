from django.contrib.auth.forms import UserCreationForm
from django.core.validators import MinLengthValidator
from django.forms.utils import ErrorList
from django.utils.safestring import mark_safe

from .models import SECURITY_QUESTIONS
from django import forms
from .models import CustomUser
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import AuthenticationForm

class CustomErrorList(ErrorList):
    def __str__(self):
        if not self:
            return ''
        return mark_safe(''.join([
            f'<div class="alert alert-danger" role="alert">{e}</div>' for e in self]))


class CustomUserCreationForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super(CustomUserCreationForm, self).__init__ (*args, **kwargs)
        for fieldname in ['username', 'password1',
        'password2']:
            self.fields[fieldname].help_text = None
            self.fields[fieldname].widget.attrs.update(
                {'class': 'form-control'}
            )

class CustomUserCreationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, validators=[MinLengthValidator(8)]) #No Validation Needed.
    confirm_password = forms.CharField(widget=forms.PasswordInput)
    security_answer_1 = forms.CharField(widget=forms.TextInput)
    security_answer_2 = forms.CharField(widget=forms.TextInput)

    # Use a choice field for questions.
    security_question_1 = forms.ChoiceField(choices=[(key, question) for key, question in SECURITY_QUESTIONS.items()], label="Security Question 1")
    security_question_2 = forms.ChoiceField(choices=[(key, question) for key, question in SECURITY_QUESTIONS.items()], label="Security Question 2")

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password', 'confirm_password', 'security_question_1', 'security_answer_1', 'security_question_2', 'security_answer_2')

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        if password and confirm_password and password != confirm_password:
            raise ValidationError("Passwords do not match.")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])  # No Hashing Now
        user.security_question_1 = self.cleaned_data['security_question_1']  # Save the question key
        user.security_question_2 = self.cleaned_data['security_question_2']  # Save the other question key
        if commit:
            user.save()
        return user


class SecurityQuestionForm(forms.Form):
    answer1 = forms.CharField(label="Answer to Question 1")
    answer2 = forms.CharField(label="Answer to Question 2")

class CustomAuthenticationForm(AuthenticationForm):
    """Custom authentication form to use email instead of username."""
    username = forms.EmailField(label="Email")