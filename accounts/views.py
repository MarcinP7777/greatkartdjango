from django.http import HttpResponse
from django.shortcuts import redirect, render
from .models import Account
from .forms import RegistrationForm
# from django.contrib.messages import constants as messages
from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required
#Verification email
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage
from django.contrib.auth import get_user_model


def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            # Pobranie danych z formularza
            first_name = form.cleaned_data['first_name']
            phone_number = form.cleaned_data['phone_number']
            last_name = form.cleaned_data['last_name']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            username = email.split("@")[0]

            # Tworzenie użytkownika
            user = Account.objects.create_user(first_name=first_name, last_name=last_name, phone_number=phone_number, email=email, username=username, password=password)
            user.save()


            # aktywacja użytkownika - bez tego użytkownik po zarejestrowaniu nie może się zalogować
            current_site = get_current_site(request)
            mail_subject = "Please activate your account"
            message = render_to_string('accounts/account_verification_email.html', {
                'user': user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user), 
            })

            to_email = email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()
            
            # Komunikat o sukcesie
            messages.success(request, 'Registration successful')
            
            # Przekierowanie (tutaj możesz zmienić na przekierowanie do strony logowania)
 #           return redirect('register')
            return redirect('/accounts/login/?command=verification&email=' + email ) 
        else:
            # Przekazanie formularza z błędami do szablonu
            context = {'form': form}
            return render(request, 'accounts/register.html', context)
    else:
        form = RegistrationForm()

    context = {'form': form}
    return render(request, 'accounts/register.html', context)



# def register(request):
#     if request.method == 'POST':
#         form = RegistrationForm(request.POST)
#         if form.is_valid():
#             # Dodaj tutaj logikę sprawdzania potwierdzenia hasła, jeśli nie jest obsłużone przez formularz
#             if form.cleaned_data['password'] != form.cleaned_data['confirm_password']:
#                 form.add_error('confirm_password', 'Password must match.')
#                 return render(request, 'accounts/register.html', {'form': form})
#             user = form.save(commit=False)
#             user.username = form.cleaned_data['email'].split("@")[0]
#             user.set_password(form.cleaned_data['password'])
#             user.is_active = True  # Ustawienie użytkownika jako aktywnego, jeśli to zamierzone
#             user.save()
            
#             # Możesz tutaj przekierować do strony logowania lub strony głównej
#             return redirect('login')  # Zakładając, że masz zdefiniowany URL o nazwie 'login'
#         else:
#             print(form.errors)  # Dodano dla debugowania
#     else:
#         form = RegistrationForm()
    
#     return render(request, 'accounts/register.html', {'form': form})


def login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = password = request.POST.get('password')

        user = auth.authenticate(email=email, password=password)

        if user is not None:
            auth.login(request, user)
 #           messages.success(request, "Your are now logged in")
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid login credetials")
            return redirect('login')
    return render(request, 'accounts/login.html')

@login_required(login_url = 'login')
def logout(request):
    auth.logout(request)
    messages.success(request, "You are now logged out")
    return redirect('login')



def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = get_user_model().objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, get_user_model().DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Congratulations! Your account is activated. You can log in now.')
        # Można tutaj dodać logikę logowania użytkownika lub przekierować do strony logowania
        return redirect('login')  # Zmienić 'login' na właściwą nazwę URL strony logowania
        
    else:
        # Opcjonalnie: przekierowanie do strony błędu
   #     return render(request, 'accounts/activation_invalid.html')
        messages.error(request, 'Invalid activation link')
        return redirect('register') 
    
@login_required(login_url = 'login')
def dashboard(request):
    return render (request, 'accounts/dashboard.html')


def forgotPassword(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        if Account.objects.filter(email=email).exists() :
            user = Account.objects.get(email__exact =email)
              # ponowna aktywacja użytkownika - bez tego użytkownik po zarejestrowaniu nie może się zalogować
            current_site = get_current_site(request)
            mail_subject = "Reset Your Password"
            message = render_to_string('accounts/reset_password_email.html', {
                'user': user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user), 
            })

            to_email = email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()

            messages.success(request, 'Password reset has been sent to Your email address')
            return redirect('login')

        else:
            messages.error(request, 'Account does not exist')
            return redirect('forgotPassword')
    return render (request, 'accounts/forgotPassword.html')

def resetpassword_validate(request, uidb64, token):
    # Twoja logika tutaj, na przykład:
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = get_user_model().objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, get_user_model().DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        # Logika, jeśli token jest poprawny, na przykład pozwól użytkownikowi ustawić nowe hasło
        #return HttpResponse('Token jest poprawny. Tutaj formularz do zmiany hasła.')
            request.session['uid'] = uid
            messages.success(request, 'Please reset Your password')
            return redirect('resetPassword')
    else:
        # Logika, jeśli token jest niepoprawny, na przykład pokaż błąd
        messages.error(request, 'This link is invalid or has expired')
        return redirect('login')

# Pamiętaj, aby również odpowiednio zaktualizować urls.py, aby przekazywał te argumenty do widoku.
    
  
def resetPassword(request):
    if request.method == 'POST':
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password == confirm_password:
             uid = request.session.get('uid')
             user = Account.objects.get(pk=uid)
             user.set_password(password)
             user.save()
             messages.success(request, "Password reset succesful")
             return redirect('login')
        
        else:
            messages.error(request, 'Password do not match')
            return redirect('resetPassword')
        
    else:
        return render(request, 'accounts/resetPassword.html')

