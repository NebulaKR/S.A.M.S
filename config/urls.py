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
    path('admin/', admin.site.urls),

    path('', sams_views.landing, name='landing'),
    path('home/', sams_views.home, name='home'),
    path('simulation/', sams_views.simulation_dashboard, name='simulation'),
    path('portfolio/', sams_views.portfolio_dashboard, name='portfolio'),
    path('trading/', sams_views.trading_view, name='trading'),

    # API endpoints
    path('api/portfolio/buy/', sams_views.buy_stock, name='api_buy_stock'),
    path('api/portfolio/sell/', sams_views.sell_stock, name='api_sell_stock'),
    path('api/portfolio/watchlist/add/', sams_views.add_to_watchlist, name='api_add_watchlist'),
    path('api/portfolio/watchlist/remove/', sams_views.remove_from_watchlist, name='api_remove_watchlist'),
    path('api/portfolio/data/', sams_views.get_portfolio_data, name='api_portfolio_data'),

    path('login/', LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),

    path('accounts/signup/', sams_views.signup, name='signup'),
    path('accounts/login/', LoginView.as_view(template_name='accounts/login.html'), name='account_login'),

    path('accounts/', include('django.contrib.auth.urls')),
]
