from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinLengthValidator
import os
# --- Removed Hashing --
# def hash_password(password):
#     # NO HASHING
#     return password #DO NOT DO THIS IN REAL LIFE

# def verify_password(password, stored_password):
#    # NO VERIFICATION
#     return password == stored_password #DO NOT DO THIS IN REAL LIFE

SECURITY_QUESTIONS = {
    '1': "What was the name of your first pet?",
    '2': "What is your mother's maiden name?",
}


class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    security_question_1 = models.CharField(max_length=1, choices=[(key, key) for key in SECURITY_QUESTIONS.keys()], blank=True, null=True)  # Store the KEY
    security_answer_1 = models.CharField(max_length=255, blank=True, null=True)
    security_question_2 = models.CharField(max_length=1, choices=[(key, key) for key in SECURITY_QUESTIONS.keys()], blank=True, null=True)  # Store the KEY
    security_answer_2 = models.CharField(max_length=255, blank=True, null=True)
    # Add related_name to resolve clash.  Choose names that are descriptive.
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text=(
            'The groups this user belongs to. A user will get all permissions '
            'granted to each of their groups.'
        ),
        related_name='customuser_set',  # ADD THIS LINE
        related_query_name='user',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name='customuser_set',  # ADD THIS LINE
        related_query_name='user',
    )

    def set_password(self, raw_password):
         # --- Removed Hashing --
        self.password = raw_password  # DO NOT DO THIS IN REAL LIFE
        pass
    def check_password(self, raw_password):
        return raw_password == self.password # NO HASHING
        pass
        # --- Removed Hashing --
        #  return verify_password(raw_password, self.password) # NO HASHING
        # pass

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']