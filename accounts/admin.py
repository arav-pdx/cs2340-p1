from django.contrib import admin
from django.contrib.auth.admin import UserAdmin # Import UserAdmin
from .models import CustomUser # Import your CustomUser model

class CustomUserAdmin(UserAdmin): # Create a CustomUserAdmin class inheriting from UserAdmin
    model = CustomUser # Specify your CustomUser model

    # Customize fieldsets to display your custom fields in the admin form
    fieldsets = UserAdmin.fieldsets + (
        ('Reset Password', {'fields': ('reset_token', 'reset_token_expiry',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('email',)}), # Add email and security questions to add form
    )

# Register your CustomUser model with the CustomUserAdmin class
admin.site.register(CustomUser, CustomUserAdmin)