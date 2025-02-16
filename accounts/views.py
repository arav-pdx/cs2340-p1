# --- django_security_questions_app/views.py ---
from django.shortcuts import render, redirect
from .forms import CustomUserCreationForm, CustomErrorList, SecurityQuestionForm
from django.contrib.auth import login as auth_login, authenticate, logout as auth_logout
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages # Add messages import
from .models import CustomUser #Import your User
# from django.contrib.auth.hashers import make_password, check_password #Import Password stuff.

# --- Security Questions -- (Defined in models.py)
# SECURITY_QUESTIONS = {
#     '1': "What was the name of your first pet?",
#     '2': "What is your mother's maiden name?",
#     # Add more questions as needed.  Use unique keys.
# }

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
        #User Authentication without password hashing
        email = request.POST.get('username') # Get the email.
        password = request.POST.get('password')
        try:
            user = User.objects.get(email=email) #Look up the user.
            if user.password == password:  # NO HASHING. Direct comparison
                auth_login(request, user)
                return redirect('home.index')
            else:
                template_data['error'] = 'The username or password is incorrect.' #Error message on incorrect password.
                return render(request, 'accounts/login.html', {'template_data': template_data})
        except User.DoesNotExist:
            template_data['error'] = 'The username or password is incorrect.' # Error message on incorrect username
            return render(request, 'accounts/login.html', {'template_data': template_data})


def forgot_password(request):
    template_data = {}
    template_data['title'] = 'Forgot Password'
    if request.method == 'GET':
        return render(request, 'accounts/forgot_password.html', {'template_data': template_data}) #Render the forgot password page
    elif request.method == 'POST':
        email = request.POST.get('email') # Get the email.
        try:
            user = User.objects.get(email=email) # Find the user.
            # Store email in session, and redirect to security questions.
            request.session['reset_email'] = email #Store Email for later use
            return redirect('security_questions')
        except User.DoesNotExist:
            # DO NOT REVEAL IF EMAIL EXISTS.
            messages.info(request, "If this email is registered, an email will be sent.") #Display generic message
            return render(request, 'accounts/forgot_password.html', {'template_data': template_data}) #Render the forgot password page.

def security_questions(request):
    template_data = {}
    template_data['title'] = 'Security Questions'
    email = request.session.get('reset_email') #get the email
    if not email:
        messages.error(request, "Invalid request.")
        return redirect('accounts.login') # Go back to login.
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        messages.error(request, "User not found.")
        return redirect('accounts.login')

    if request.method == 'POST':
        form = SecurityQuestionForm(request.POST) #Use our security form.
        if form.is_valid():
            answer1 = form.cleaned_data['answer1']
            answer2 = form.cleaned_data['answer2']

            # Validate answers. - Access answers directly from the user model.
            if (answer1.lower() == user.security_answer_1.lower() and
                answer2.lower() == user.security_answer_2.lower()):
                #Correct answers, store user ID in session and redirect.
                request.session['user_id_to_reset'] = user.id
                return redirect('reset_password') #go to reset password
            else:
                messages.error(request, "Incorrect answers.") #Show incorrect answer error
    else:
        #Render security question form
        form = SecurityQuestionForm() # Create an empty form.

    # Pass the questions to the template in context.
    template_data['form'] = form
    template_data['question1'] = CustomUser.SECURITY_QUESTIONS.get(user.security_question_1)
    template_data['question2'] = CustomUser.SECURITY_QUESTIONS.get(user.security_question_2) #get the other question.

    return render(request, 'accounts/security_questions.html', {'template_data': template_data})

def reset_password(request):
    template_data = {}
    template_data['title'] = 'Reset Password'
    user_id_to_reset = request.session.get('user_id_to_reset')
    if not user_id_to_reset:
        messages.error(request, "Invalid request. Please initiate the password reset process again.")
        return redirect('forgot_password')  # Start over

    try:
        user = User.objects.get(pk=user_id_to_reset)
    except User.DoesNotExist:
        messages.error(request, "User not found for password reset.")
        return redirect('forgot_password')  # Start over.

    if request.method == 'POST':
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
        else:
            # --- Removed Hashing --
            user.set_password(password)
            user.save()
            # --- Removed Hashing --
            # user.password = password # DO NOT DO THIS IN REAL LIFE
            # user.save()

            # Clear the session
            del request.session['user_id_to_reset']
            del request.session['reset_email']
            messages.success(request, "Your password has been reset. Please log in.")
            return redirect('accounts.login')  # Redirect to login

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