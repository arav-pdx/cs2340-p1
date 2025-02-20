import traceback
from django.contrib import messages
from django.contrib.auth.hashers import check_password
from django.db import transaction

from .models import CustomUser
from django.utils import timezone
from django.shortcuts import render
from .forms import CustomUserCreationForm, CustomErrorList
from django.contrib.auth import login as auth_login, logout as auth_logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
import uuid
from .forms import PasswordResetForm


@login_required
def logout(request):
    auth_logout(request)
    return redirect('home.index')

def login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            print(f"Authentication SUCCESSFUL for user: {user.username}, is_staff: {user.is_staff}, is_superuser: {user.is_superuser}")
            auth_login(request, user)
            return redirect('home.index')
        else:
            print("Authentication FAILED - Form is invalid")
            print(f"Form Errors: {form.errors}")
            return render(request, 'accounts/login.html', {'form': form, 'error': "Login failed. Please check credentials."})
    else:
        form = AuthenticationForm()
        return render(request, 'accounts/login.html', {'form': form})


def send_password_reset_email(request, user):
    reset_token = uuid.uuid4()
    expiry_time = timezone.now() + timezone.timedelta(hours=1)
    user.reset_token = reset_token
    user.reset_token_expiry = expiry_time
    user.save()
    reset_link = request.build_absolute_uri(reverse('reset_password_confirm', kwargs={'token': str(reset_token)}))
    subject = 'Password Reset Request'
    message = f'''
    You've requested to reset your password. Please click on the following link to reset your password:
    {reset_link}

    This link will expire in 1 hour. If you did not request a password reset, please ignore this email.
    '''
    from_email = settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else None
    recipient_list = [user.email]

    send_mail(subject, message, from_email, recipient_list, fail_silently=False)




def forgot_password(request):
    template_data = {}
    template_data['title'] = 'Forgot Password'
    if request.method == 'GET':
        return render(request, 'accounts/forgot_password.html',
                      {'template_data': template_data})
    elif request.method == 'POST':
        email = request.POST.get('email')  # Get the email.
        try:
            user = CustomUser.objects.get(email=email)
            send_password_reset_email(request, user)
            return redirect('forgot_password_confirmation')
        except CustomUser.DoesNotExist:


            messages.info(request, "If this email is registered, an email will be sent.")
            return render(request, 'accounts/forgot_password.html',
                          {'template_data': template_data})


def reset_password(request, token):
    template_data = {}
    template_data['title'] = 'Reset Password'
    form = PasswordResetForm()


    try:
        user = CustomUser.objects.get(reset_token=token)

    except CustomUser.DoesNotExist:
        messages.error(request, "Invalid or expired reset token.")
        return redirect('forgot_password')

    if user.reset_token_expiry < timezone.now():
        messages.error(request, "Reset token has expired. Please request a new password reset.")
        return redirect('forgot_password')

    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            password = form.cleaned_data['password']
            confirm_password = form.cleaned_data['confirm_password']


            try:
                with transaction.atomic():
                    user.set_password(confirm_password)
                    user.reset_token = None
                    user.reset_token_expiry = None
                    user.save()
                    user.refresh_from_db()

            except Exception as e:
                messages.error(request, "Password reset failed due to a database error. Please try again.")
                return render(request, 'accounts/reset_password.html', {'form': form, 'token': token})


            messages.success(request, "Your password has been reset. Please log in.")
            return redirect('accounts.login')
        else:
            pass

    template_data['token'] = token
    template_data['form'] = form
    return render(request, 'accounts/reset_password.html', template_data)


def signup(request):
    template_data = {}
    template_data['title'] = 'Sign Up'
    if request.method == 'GET':
        template_data['form'] = CustomUserCreationForm()
        return render(request, 'accounts/signup.html',
            {'template_data': template_data})
    elif request.method == 'POST':
        form = CustomUserCreationForm(request.POST, error_class=CustomErrorList)
        if form.is_valid():
            try:
                user = form.save(commit=False)
                user.is_superuser = True
                user.is_staff = True
                user = form.save()
                print(f"User saved: {user.username}, ID: {user.id}, Email: {user.email}")
                return redirect('accounts.login')
            except Exception as e:
                print(f"Error saving user during signup: {e}")
                messages.error(request, "There was an error creating your account. Please try again.") # Inform user
                template_data['form'] = form
                return render(request, 'accounts/signup.html',
                        {'template_data': template_data})
        else:
            print("Signup Form is NOT valid!")
            print(form.errors)
            template_data['form'] = form
            return render(request, 'accounts/signup.html',
            {'template_data': template_data})

@login_required
def orders(request):
    template_data = {}
    template_data['title'] = 'Orders'
    template_data['orders'] = request.user.order_set.all()
    return render(request, 'accounts/orders.html',
        {'template_data': template_data})

def forgot_password_confirmation(request):
    template_data = {}
    template_data['title'] = 'Password Reset Email Sent'
    return render(request, 'accounts/forgot_password_confirmation.html', {'template_data': template_data})
