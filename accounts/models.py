from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinLengthValidator
import os

SECURITY_QUESTIONS = {
    '1': "What was the name of your first pet?",
    '2': "What is your mother's maiden name?",
}


class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    security_question_1 = models.CharField(max_length=1, choices=[(key, key) for key in SECURITY_QUESTIONS.keys()], blank=True, null=True)
    security_answer_1 = models.CharField(max_length=255, blank=True, null=True)
    security_question_2 = models.CharField(max_length=1, choices=[(key, key) for key in SECURITY_QUESTIONS.keys()], blank=True, null=True)
    security_answer_2 = models.CharField(max_length=255, blank=True, null=True)
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text=(
            'The groups this user belongs to. A user will get all permissions '
            'granted to each of their groups.'
        ),
        related_name='customuser_set',
        related_query_name='user',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name='customuser_set',
        related_query_name='user',
    )

    def set_password(self, raw_password):
        self.password = raw_password
        pass
    def check_password(self, raw_password):
        return raw_password == self.password
        pass

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']