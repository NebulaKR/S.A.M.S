from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login as auth_login
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from decimal import Decimal
import json

from .services import PortfolioService, StockService
from .models import Stock

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

@login_required
def simulation_dashboard(request):
    """시뮬레이션 대시보드"""
    context = {
        'simulation_active': True,
    }
    return render(request, 'app/simulation_dashboard.html', context)

@login_required
def portfolio_dashboard(request):
    """포트폴리오 대시보드"""
    portfolio_summary = PortfolioService.get_portfolio_summary(request.user)
    all_stocks = StockService.get_all_stocks()
    watchlist = PortfolioService.get_watchlist(request.user)
    
    context = {
        'portfolio': portfolio_summary,
        'all_stocks': all_stocks,
        'watchlist': watchlist,
    }
    return render(request, 'app/portfolio_dashboard.html', context)

@login_required
def trading_view(request):
    """거래 화면"""
    all_stocks = StockService.get_all_stocks()
    portfolio_summary = PortfolioService.get_portfolio_summary(request.user)
    
    context = {
        'all_stocks': all_stocks,
        'portfolio': portfolio_summary,
    }
    return render(request, 'app/trading_view.html', context)

@login_required
@require_POST
def buy_stock(request):
    """주식 매수 API"""
    try:
        data = json.loads(request.body)
        ticker = data.get('ticker')
        quantity = int(data.get('quantity', 0))
        price = Decimal(data.get('price', 0))
        
        if not all([ticker, quantity, price]):
            return JsonResponse({'success': False, 'message': '필수 파라미터가 누락되었습니다'})
        
        result = PortfolioService.buy_stock(request.user, ticker, quantity, price)
        return JsonResponse(result)
        
    except ValueError as e:
        return JsonResponse({'success': False, 'message': str(e)})
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'매수 중 오류가 발생했습니다: {str(e)}'})

@login_required
@require_POST
def sell_stock(request):
    """주식 매도 API"""
    try:
        data = json.loads(request.body)
        ticker = data.get('ticker')
        quantity = int(data.get('quantity', 0))
        price = Decimal(data.get('price', 0))
        
        if not all([ticker, quantity, price]):
            return JsonResponse({'success': False, 'message': '필수 파라미터가 누락되었습니다'})
        
        result = PortfolioService.sell_stock(request.user, ticker, quantity, price)
        return JsonResponse(result)
        
    except ValueError as e:
        return JsonResponse({'success': False, 'message': str(e)})
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'매도 중 오류가 발생했습니다: {str(e)}'})

@login_required
@require_POST
def add_to_watchlist(request):
    """관심종목 추가 API"""
    try:
        data = json.loads(request.body)
        ticker = data.get('ticker')
        
        if not ticker:
            return JsonResponse({'success': False, 'message': '종목 코드가 누락되었습니다'})
        
        result = PortfolioService.add_to_watchlist(request.user, ticker)
        return JsonResponse(result)
        
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'관심종목 추가 중 오류가 발생했습니다: {str(e)}'})

@login_required
@require_POST
def remove_from_watchlist(request):
    """관심종목 제거 API"""
    try:
        data = json.loads(request.body)
        ticker = data.get('ticker')
        
        if not ticker:
            return JsonResponse({'success': False, 'message': '종목 코드가 누락되었습니다'})
        
        result = PortfolioService.remove_from_watchlist(request.user, ticker)
        return JsonResponse(result)
        
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'관심종목 제거 중 오류가 발생했습니다: {str(e)}'})

@login_required
def get_portfolio_data(request):
    """포트폴리오 데이터 API"""
    try:
        portfolio_summary = PortfolioService.get_portfolio_summary(request.user)
        return JsonResponse({
            'success': True,
            'data': {
                'total_value': float(portfolio_summary['total_value']),
                'total_return': float(portfolio_summary['total_return']),
                'cash_balance': float(portfolio_summary['cash_balance']),
                'cash_ratio': float(portfolio_summary['cash_ratio']),
                'stock_value': float(portfolio_summary['stock_value']),
                'unrealized_pnl': float(portfolio_summary['unrealized_pnl']),
                'positions': portfolio_summary['positions']
            }
        })
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'포트폴리오 데이터 조회 중 오류가 발생했습니다: {str(e)}'})
