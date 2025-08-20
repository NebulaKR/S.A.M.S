from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from decimal import Decimal


class Portfolio(models.Model):
    """사용자 포트폴리오"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='portfolio')
    name = models.CharField(max_length=100, default='내 포트폴리오')
    initial_balance = models.DecimalField(max_digits=15, decimal_places=2, default=10000000)  # 1천만원
    current_balance = models.DecimalField(max_digits=15, decimal_places=2, default=10000000)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username}의 포트폴리오"
    
    @property
    def total_value(self):
        """총 자산 가치 (현금 + 주식)"""
        stock_value = sum(position.current_value for position in self.positions.all())
        return self.current_balance + stock_value
    
    @property
    def total_return(self):
        """총 수익률"""
        if self.initial_balance == 0:
            return Decimal('0.00')
        return ((self.total_value - self.initial_balance) / self.initial_balance) * 100
    
    @property
    def cash_ratio(self):
        """현금 비중"""
        if self.total_value == 0:
            return Decimal('0.00')
        return (self.current_balance / self.total_value) * 100


class Stock(models.Model):
    """주식 정보"""
    ticker = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100)
    sector = models.CharField(max_length=50, blank=True)
    current_price = models.DecimalField(max_digits=10, decimal_places=2)
    base_price = models.DecimalField(max_digits=10, decimal_places=2)  # 시뮬레이션 시작 시 가격
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} ({self.ticker})"
    
    @property
    def price_change(self):
        """가격 변화율"""
        if self.base_price == 0:
            return Decimal('0.00')
        return ((self.current_price - self.base_price) / self.base_price) * 100


class Position(models.Model):
    """포트폴리오 내 주식 포지션"""
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, related_name='positions')
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    quantity = models.IntegerField(validators=[MinValueValidator(0)])
    average_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['portfolio', 'stock']
    
    def __str__(self):
        return f"{self.portfolio.user.username}의 {self.stock.name} {self.quantity}주"
    
    @property
    def current_value(self):
        """현재 가치"""
        return self.quantity * self.stock.current_price
    
    @property
    def unrealized_pnl(self):
        """미실현 손익"""
        return self.current_value - (self.quantity * self.average_price)
    
    @property
    def unrealized_pnl_percent(self):
        """미실현 손익률"""
        if self.quantity * self.average_price == 0:
            return Decimal('0.00')
        return (self.unrealized_pnl / (self.quantity * self.average_price)) * 100


class Transaction(models.Model):
    """거래 내역"""
    TRANSACTION_TYPES = [
        ('BUY', '매수'),
        ('SELL', '매도'),
        ('DEPOSIT', '입금'),
        ('WITHDRAWAL', '출금'),
    ]
    
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, related_name='transactions')
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, null=True, blank=True)
    quantity = models.IntegerField(null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    amount = models.DecimalField(max_digits=15, decimal_places=2)  # 총 거래 금액
    balance_before = models.DecimalField(max_digits=15, decimal_places=2)  # 거래 전 잔고
    balance_after = models.DecimalField(max_digits=15, decimal_places=2)   # 거래 후 잔고
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        if self.stock:
            return f"{self.get_transaction_type_display()} {self.stock.name} {self.quantity}주"
        return f"{self.get_transaction_type_display()} {self.amount:,.0f}원"
    
    @property
    def description(self):
        """거래 설명"""
        if self.transaction_type in ['BUY', 'SELL']:
            return f"{self.get_transaction_type_display()} {self.stock.name} {self.quantity}주 @ ₩{self.price:,.0f}"
        else:
            return f"{self.get_transaction_type_display()} {self.amount:,.0f}원"


class Watchlist(models.Model):
    """관심종목"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='watchlists')
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'stock']
    
    def __str__(self):
        return f"{self.user.username}의 관심종목: {self.stock.name}"
