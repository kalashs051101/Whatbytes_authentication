from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login,logout
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.models import User
from .forms import SignUpForm,LoginForm,ChangePasswordForm,CustomPasswordResetForm,ForgotCustomPasswordResetForm
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.tokens import default_token_generator



def home_view(request):
    return render(request,'home.html')


def signup_view(request):
    try:
        if request.method == "POST":
            form = SignUpForm(request.POST)
            if form.is_valid():
                user = form.save(commit=False)
                user.set_password(form.cleaned_data['password']) 
                user.save()
                return redirect('login')
            else:
                print(form.errors)
        else:
            form = SignUpForm()
    except Exception as e:
        messages.error(request,f'{str(e)}')
    return render(request, 'signup.html', {'form': form})


def login_view(request):
    try:

        if request.method == 'POST':
            print('post')
            form = LoginForm(request.POST)
            if form.is_valid():
                email = form.cleaned_data['email']
                password = form.cleaned_data['password']
                print('form valid')
                
                try:
                    user = User.objects.get(email=email)
                    print(f'Found user with email: {email}')
                    
                    user = authenticate(request, username=user.username, password=password)
                    
                    if user is not None:
                        login(request, user)
                        messages.success(request, "Welcome back, you are now logged in!")
                        return redirect('dashboard')  
                    else:
                        
                        messages.error(request, "Invalid credentials, please try again.")

                except User.DoesNotExist:
                    messages.error(request, "No account found with this email.")
            else:
                print('not valid')
                print(form.errors)
        else:
            form = LoginForm()

    except Exception as e:
        messages.error(request,f'{str(e)}')

    return render(request, 'login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')  



@login_required
def change_password_view(request):
    try:

        if request.method == "POST":
            form = ChangePasswordForm(request.POST)
            if form.is_valid():
                user = request.user
                old_password = form.cleaned_data.get('old_password')
                if user.check_password(old_password):
                    user.set_password(form.cleaned_data.get('new_password'))
                    user.save()
                    update_session_auth_hash(request, user)  
                    messages.success(request, "Your password has been updated successfully!")
                    return redirect('dashboard')  
                else:
                    form.add_error('old_password', "The old password is incorrect.")
        else:
            form = ChangePasswordForm()
    except Exception as e:
        messages.error(request,f'{str(e)}')
    return render(request, 'change_password.html', {'form': form})


@login_required
def dashboard_view(request):
    return render(request,'dashboard.html')


def forgot_password_view(request):
    try:

        if request.method == 'POST':
            form = ForgotCustomPasswordResetForm(request.POST)
            if form.is_valid():
                email = form.cleaned_data['email']
                try:
                    user = User.objects.get(email=email)
                    
                    uidb64 = urlsafe_base64_encode(str(user.id).encode())                    
                    token = default_token_generator.make_token(user)

                    reset_link = request.build_absolute_uri(f'/reset-password/{uidb64}-{token}/')
                    print(uidb64)
                    print(token)

                    print('reset_link: ',reset_link)
                    
                    send_mail(          #send mail
                        'Password Reset Request',
                        f'Click the link to reset your password: {reset_link}',
                        settings.EMAIL_HOST_USER,
                        [email]
                    )
                    messages.success(request, 'password reset link sent to your mail')
                    return redirect('login')
                except User.DoesNotExist:
                    messages.error(request, 'No account with that email exists.')
        else:
            form = ForgotCustomPasswordResetForm()
    except Exception as e:
        messages.error(request,f'{str(e)}')
    return render(request, 'forgot_password.html', {'form': form})


def reset_password_view(request, token):
    try:
        token_parts = token.split("-")
        
        if len(token_parts) < 2:
            messages.error(request, 'The password reset link invalid')
            return redirect('forgot_password')
        
        uidb64, reset_token = token_parts[0], "-".join(token_parts[1:]) 
        print('i a here')

        uid = urlsafe_base64_decode(uidb64).decode('utf-8')
        user = get_object_or_404(User, pk=uid)
        print(token)
        print(uidb64)


        if default_token_generator.check_token(user, reset_token):   #validate
            if request.method == 'POST':
                form = CustomPasswordResetForm(request.POST)

                if form.is_valid():
                    new_password = form.cleaned_data['password']
                    user.set_password(new_password)
                    user.save()

                    messages.success(request, "Your password reset successfully!")
                    return redirect('login')
            else:
                form = CustomPasswordResetForm()

        else:
            messages.error(request, 'The password reset link expired.')
            return redirect('forgot_password')

    except ValueError:
        print( 'The password reset link is malformed or invalid.')
        messages.error(request, 'The password reset link is malformed or invalid.')
        return redirect('forgot_password')

    except User.DoesNotExist:
        messages.error(request, 'The user does not exist.')
        return redirect('forgot_password')
    except Exception as e:
        print(f"Error: {str(e)}")
        messages.error(request, f"error: {str(e)}")
        return redirect('forgot_password')
    return render(request, 'reset_password.html', {'form': form, 'token': token})


@login_required
def profile_view(request):    
    try:

        profile = request.user.profile  
        print(profile)
        print(profile.last_updated)
        context = {
            # 'username': request.user.username,
            # 'email': request.user.email,
            # 'date_joined': request.user.date_joined,
            'last_updated': profile.last_updated,
        }
    except Exception as e:
        print(f"rrror is: {str(e)}")
        messages.error(request, f"error is: {str(e)}")
    
    return render(request,'profile.html',context)



