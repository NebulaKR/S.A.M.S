from django.contrib import admin
from .models import Portfolio, Stock, Position, Transaction, Watchlist


@admin.register(Portfolio)
class PortfolioAdmin(admin.ModelAdmin):
    list_display = ['user', 'name', 'initial_balance', 'current_balance', 'total_value', 'total_return', 'cash_ratio', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'name']
    readonly_fields = ['total_value', 'total_return', 'cash_ratio']


@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ['ticker', 'name', 'sector', 'current_price', 'base_price', 'price_change', 'updated_at']
    list_filter = ['sector', 'updated_at']
    search_fields = ['ticker', 'name']
    readonly_fields = ['price_change']


@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    list_display = ['portfolio', 'stock', 'quantity', 'average_price', 'current_value', 'unrealized_pnl', 'unrealized_pnl_percent']
    list_filter = ['created_at']
    search_fields = ['portfolio__user__username', 'stock__name']
    readonly_fields = ['current_value', 'unrealized_pnl', 'unrealized_pnl_percent']


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['portfolio', 'transaction_type', 'stock', 'quantity', 'price', 'amount', 'balance_after', 'created_at']
    list_filter = ['transaction_type', 'created_at']
    search_fields = ['portfolio__user__username', 'stock__name']
    readonly_fields = ['balance_before', 'balance_after']


@admin.register(Watchlist)
class WatchlistAdmin(admin.ModelAdmin):
    list_display = ['user', 'stock', 'added_at']
    list_filter = ['added_at']
    search_fields = ['user__username', 'stock__name']
