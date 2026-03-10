
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render, redirect, get_object_or_404

from django.views.decorators.csrf import csrf_protect, csrf_exempt


def message(request):
    return render(request, 'main/message.html')


# @csrf_protect
def login_view(request):
    next_url = request.GET.get('next') or request.POST.get('next') or 'home'
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')
    else:
        form = AuthenticationForm(request)

    # Подавам form за да покажа грешки/values без да променям визията
    return render(request, 'main/sign-in.html', {'form': form, 'next': next_url})
