"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth.views import LoginView, LogoutView
from sams import views as sams_views

urlpatterns = [
    path('django-admin/', admin.site.urls),

    path('', sams_views.landing, name='landing'),
    path('home/', sams_views.home, name='home'),
    path('simulation/', sams_views.simulation_dashboard, name='simulation'),
    path('news/', sams_views.news_dashboard, name='news'),
    path('admin/', sams_views.admin_dashboard, name='admin'),
    path('portfolio/', sams_views.portfolio_dashboard, name='portfolio'),
    path('trading/', sams_views.trading_view, name='trading'),
    path('realtime/', sams_views.realtime_dashboard, name='realtime'),

    # 기존 API endpoints
    path('api/portfolio/buy/', sams_views.buy_stock, name='api_buy_stock'),
    path('api/portfolio/sell/', sams_views.sell_stock, name='api_sell_stock'),
    path('api/portfolio/watchlist/add/', sams_views.add_to_watchlist, name='api_add_watchlist'),
    path('api/portfolio/watchlist/remove/', sams_views.remove_from_watchlist, name='api_remove_watchlist'),
    path('api/portfolio/data/', sams_views.get_portfolio_data, name='api_portfolio_data'),
    
    # 새로운 거래 API 엔드포인트
    path('api/trading/buy/', sams_views.buy_stock_api, name='api_trading_buy'),
    path('api/trading/sell/', sams_views.sell_stock_api, name='api_trading_sell'),

    # 파이어베이스 시뮬레이션 데이터 API 엔드포인트들
    path('api/simulation/status/', sams_views.get_simulation_status, name='api_simulation_status'),
    path('api/simulation/events/', sams_views.get_recent_events, name='api_recent_events'),
    path('api/simulation/events/detail/', sams_views.get_event_detail, name='api_event_detail'),
    path('api/simulation/news/', sams_views.get_news_feed, name='api_news_feed'),
    path('api/simulation/market-summary/', sams_views.get_market_summary, name='api_market_summary'),

    # 관리자 시뮬레이션 제어 API 엔드포인트들
    path('api/admin/simulation/start/', sams_views.start_simulation, name='api_start_simulation'),
    path('api/admin/simulation/pause/', sams_views.pause_simulation, name='api_pause_simulation'),
    path('api/admin/simulation/stop/', sams_views.stop_simulation, name='api_stop_simulation'),
    path('api/admin/simulation/status/', sams_views.get_simulation_control_status, name='api_simulation_control_status'),
    path('api/admin/simulation/logs/', sams_views.get_simulation_logs, name='api_simulation_logs'),
    path('api/admin/simulation/settings/', sams_views.update_simulation_settings, name='api_update_simulation_settings'),
    
    # 백그라운드 시뮬레이션 제어 API 엔드포인트들
    path('api/admin/background-simulation/start/', sams_views.start_background_simulation, name='api_start_background_simulation'),
    path('api/admin/background-simulation/stop/', sams_views.stop_background_simulation, name='api_stop_background_simulation'),
    path('api/admin/background-simulation/status/', sams_views.get_background_simulation_status, name='api_background_simulation_status'),
    
    # 실시간 주가 데이터 API 엔드포인트들
    path('api/stocks/realtime/', sams_views.get_realtime_stock_data, name='api_realtime_stock_data'),
    path('api/stocks/chart/', sams_views.get_stock_chart_data, name='api_stock_chart_data'),

    path('login/', LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),

    path('accounts/signup/', sams_views.signup, name='signup'),
    path('accounts/login/', LoginView.as_view(template_name='accounts/login.html'), name='account_login'),

    path('accounts/', include('django.contrib.auth.urls')),
]
