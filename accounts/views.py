from django.shortcuts import render, redirect
from .forms import CustomUserCreationForm, CustomErrorList, SecurityQuestionForm
from django.contrib.auth import login as auth_login, authenticate, logout as auth_logout
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from .models import CustomUser


@login_required
def logout(request):
    auth_logout(request)
    return redirect('home.index')

def login(request):
    template_data = {}
    template_data['title'] = 'Login'
    if request.method == 'GET':
        return render(request, 'accounts/login.html',
            {'template_data': template_data})
    elif request.method == 'POST':
        email = request.POST.get('username')
        password = request.POST.get('password')
        try:
            user = User.objects.get(email=email)
            if user.password == password:
                auth_login(request, user)
                return redirect('home.index')
            else:
                template_data['error'] = 'The username or password is incorrect.'
                return render(request, 'accounts/login.html', {'template_data': template_data})
        except User.DoesNotExist:
            template_data['error'] = 'The username or password is incorrect.'
            return render(request, 'accounts/login.html', {'template_data': template_data})


def forgot_password(request):
    template_data = {}
    template_data['title'] = 'Forgot Password'
    if request.method == 'GET':
        return render(request, 'accounts/forgot_password.html', {'template_data': template_data})
    elif request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
            request.session['reset_email'] = email
            return redirect('security_questions')
        except User.DoesNotExist:
            messages.info(request, "If this email is registered, an email will be sent.")
            return render(request, 'accounts/forgot_password.html', {'template_data': template_data})

def security_questions(request):
    template_data = {}
    template_data['title'] = 'Security Questions'
    email = request.session.get('reset_email')
    if not email:
        messages.error(request, "Invalid request.")
        return redirect('accounts.login')
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        messages.error(request, "User not found.")
        return redirect('accounts.login')

    if request.method == 'POST':
        form = SecurityQuestionForm(request.POST)
        if form.is_valid():
            answer1 = form.cleaned_data['answer1']
            answer2 = form.cleaned_data['answer2']

            if (answer1.lower() == user.security_answer_1.lower() and
                answer2.lower() == user.security_answer_2.lower()):
                request.session['user_id_to_reset'] = user.id
                return redirect('reset_password')
            else:
                messages.error(request, "Incorrect answers.")
    else:
        form = SecurityQuestionForm()

    template_data['form'] = form
    template_data['question1'] = CustomUser.SECURITY_QUESTIONS.get(user.security_question_1)
    template_data['question2'] = CustomUser.SECURITY_QUESTIONS.get(user.security_question_2)

    return render(request, 'accounts/security_questions.html', {'template_data': template_data})

def reset_password(request):
    template_data = {}
    template_data['title'] = 'Reset Password'
    user_id_to_reset = request.session.get('user_id_to_reset')
    if not user_id_to_reset:
        messages.error(request, "Invalid request. Please initiate the password reset process again.")
        return redirect('forgot_password')

    try:
        user = User.objects.get(pk=user_id_to_reset)
    except User.DoesNotExist:
        messages.error(request, "User not found for password reset.")
        return redirect('forgot_password')

    if request.method == 'POST':
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
        else:
            user.set_password(password)
            user.save()

            del request.session['user_id_to_reset']
            del request.session['reset_email']
            messages.success(request, "Your password has been reset. Please log in.")
            return redirect('accounts.login')

    return render(request, 'accounts/reset_password.html', {'template_data': template_data})

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
            form.save()
            return redirect('accounts.login')
        else:
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