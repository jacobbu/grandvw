from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from .forms import SignupForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import render


def signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)

        if form.is_valid():
            user = form.save()
            authenticate(username=user.username, password=user.password)

            if user is not None:
                login(request, user)

                return redirect ('/dashboard')
            
    else:
        form = SignupForm()

    return render(request, 'accounts/signup.html', {
        'form': form
    })

@login_required
def account_details(request):
    user = request.user
    return render(request, 'core/account_details.html', {'user': user})
