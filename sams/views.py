from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login as auth_login

def landing(request):
    return render(request, 'landing.html')

class MyLoginView(LoginView):
    template_name = 'accounts/login.html'

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'accounts/signup.html', {'form': form})

@login_required
def home(request):
    context = {
        'kpi': {'total_asset': '₩ 12,540,000', 'daily_change': '+1.8%', 'cash_ratio': '24%', 'beta': '0.92'},
        'watchlist': [
            {'name':'삼성전자','price':'₩ 79,800','change':'+2.1%','pos':'100주','up':True},
            {'name':'NVIDIA','price':'$ 128.30','change':'-0.6%','pos':'—','up':False},
            {'name':'Tesla','price':'$ 238.10','change':'+0.8%','pos':'10주','up':True},
        ],
    }
    return render(request, 'app/home.html', context)
