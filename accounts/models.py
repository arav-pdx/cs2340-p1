from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']
    email = models.EmailField(unique=True)
    reset_token = models.CharField(max_length=100, blank=True, null=True)
    reset_token_expiry = models.DateTimeField(blank=True, null=True)
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

