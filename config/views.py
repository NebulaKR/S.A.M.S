from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

def landing(request):
    return render(request, 'landing.html')

def login_view(request):
    if request.method == 'POST':
        return redirect('home')
    return render(request, 'account/login.html')

@login_required(login_url='login')
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
