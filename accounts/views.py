from django.contrib import messages,auth
from django.contrib.auth.decorators import login_required


#verification email
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode,urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage
from django.http import HttpResponse


from django.shortcuts import render, redirect
from .forms import RegistrationForms  # Adjust import based on your project structure
from .models import Account  # Your user model
from django.contrib import messages
from django.core.mail import EmailMessage
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.template.loader import render_to_string
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
import random

from django.shortcuts import render, redirect
from .models import Account  # Import your Account model



def register(request):
    if request.method == 'POST':
        form = RegistrationForms(request.POST)
        if form.is_valid():
            
            # Temporarily store data in session
            request.session['reg_data'] = {
                'first_name': form.cleaned_data['first_name'],
                'last_name': form.cleaned_data['last_name'],
                'phone_number': form.cleaned_data['phone_number'],
                'email': form.cleaned_data['email'],
                'password': form.cleaned_data['password'],
                'username': form.cleaned_data['email'].split("@")[0],
            } 

            otp = str(random.randint(100000, 999999))
            request.session['otp'] = otp
            
            # User activation email logic goes here...
            mail_subject = 'Your OTP for verification'
            message = f"Hello {form.cleaned_data['first_name']},\n\nYour OTP is: {otp}"
            send_email = EmailMessage(mail_subject, message, to=[form.cleaned_data['email']])
            send_email.send()
            
            messages.info(request, 'OTP has been sent to your email.')
            return redirect('verify_otp')
    else:
        form = RegistrationForms()

    context = {
        'form': form,
    }
    return render(request, 'Accounts/register.html', context)



def verify_otp(request):
    if request.method == 'POST':
        entered_otp = request.POST.get('otp')
        session_otp = request.session.get('otp')
        reg_data = request.session.get('reg_data')
        
        if entered_otp == session_otp:
            try:
                # Check if user already exists (edge case)
                if Account.objects.filter(email=reg_data['email']).exists():
                    messages.warning(request, 'User with this email already exists.')
                    return redirect('login')
                
                # Create user now
                user = Account.objects.create_user(
                    first_name=reg_data['first_name'],
                    last_name=reg_data['last_name'],
                    email=reg_data['email'],
                    username=reg_data['username'],
                    password=reg_data['password']
                )
                user.phone_number = reg_data['phone_number']
                user.is_active = True
                user.save()
                # Clean session
                del request.session['otp']
                del request.session['reg_data']
                
                messages.success(request, 'Account verified successfully. You can now login.')
                return redirect('login')
            except Exception as e:
                messages.error(request, f'Error creating account: {str(e)}')    
        else:
            messages.error(request, 'Invalid OTP. Please try again.')

    return render(request, 'accounts/verify_otp.html')


def login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        user = auth.authenticate(email=email, password=password)
        print("Authenticated User:", user)

        if user is not None:
            # If no cart exists for the session, do nothing
            auth.login(request, user)  # Log the user in
            messages.success(request, 'You are now logged in')
            return redirect('home')  # Redirect to the home page after login
        else:
            messages.error(request, 'Invalid login credentials')
            return redirect('login')
    return render(request, 'Accounts/login.html')



@login_required(login_url = 'login')
def logout(request):
    auth.logout(request)
    messages.success(request,'you are logged out!')
    return redirect('login')