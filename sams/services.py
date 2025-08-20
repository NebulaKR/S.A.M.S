from decimal import Decimal
from django.db import transaction
from django.contrib.auth.models import User
from .models import Portfolio, Stock, Position, Transaction, Watchlist


class PortfolioService:
    """포트폴리오 관리 서비스"""
    
    @staticmethod
    def get_or_create_portfolio(user: User) -> Portfolio:
        """사용자의 포트폴리오를 가져오거나 생성"""
        portfolio, created = Portfolio.objects.get_or_create(
            user=user,
            defaults={
                'name': f'{user.username}의 포트폴리오',
                'initial_balance': Decimal('10000000'),  # 1천만원
                'current_balance': Decimal('10000000')
            }
        )
        return portfolio
    
    @staticmethod
    def buy_stock(user: User, ticker: str, quantity: int, price: Decimal) -> dict:
        """주식 매수"""
        with transaction.atomic():
            portfolio = PortfolioService.get_or_create_portfolio(user)
            stock = Stock.objects.get(ticker=ticker)
            
            # 매수 금액 계산
            total_amount = quantity * price
            
            # 잔고 확인
            if portfolio.current_balance < total_amount:
                raise ValueError("잔고가 부족합니다")
            
            # 거래 전 잔고
            balance_before = portfolio.current_balance
            
            # 잔고 차감
            portfolio.current_balance -= total_amount
            portfolio.save()
            
            # 거래 후 잔고
            balance_after = portfolio.current_balance
            
            # 포지션 생성 또는 업데이트
            position, created = Position.objects.get_or_create(
                portfolio=portfolio,
                stock=stock,
                defaults={
                    'quantity': quantity,
                    'average_price': price
                }
            )
            
            if not created:
                # 기존 포지션이 있는 경우 평균 매수가 계산
                total_quantity = position.quantity + quantity
                total_cost = (position.quantity * position.average_price) + total_amount
                position.quantity = total_quantity
                position.average_price = total_cost / total_quantity
                position.save()
            
            # 거래 내역 기록
            Transaction.objects.create(
                portfolio=portfolio,
                transaction_type='BUY',
                stock=stock,
                quantity=quantity,
                price=price,
                amount=total_amount,
                balance_before=balance_before,
                balance_after=balance_after
            )
            
            return {
                'success': True,
                'message': f'{stock.name} {quantity}주 매수 완료',
                'position': position,
                'new_balance': balance_after
            }
    
    @staticmethod
    def sell_stock(user: User, ticker: str, quantity: int, price: Decimal) -> dict:
        """주식 매도"""
        with transaction.atomic():
            portfolio = PortfolioService.get_or_create_portfolio(user)
            stock = Stock.objects.get(ticker=ticker)
            
            # 포지션 확인
            try:
                position = Position.objects.get(portfolio=portfolio, stock=stock)
            except Position.DoesNotExist:
                raise ValueError("보유하지 않은 주식입니다")
            
            # 보유 수량 확인
            if position.quantity < quantity:
                raise ValueError("보유 수량이 부족합니다")
            
            # 매도 금액 계산
            total_amount = quantity * price
            
            # 거래 전 잔고
            balance_before = portfolio.current_balance
            
            # 잔고 증가
            portfolio.current_balance += total_amount
            portfolio.save()
            
            # 거래 후 잔고
            balance_after = portfolio.current_balance
            
            # 포지션 업데이트
            if position.quantity == quantity:
                # 전량 매도
                position.delete()
            else:
                # 부분 매도
                position.quantity -= quantity
                position.save()
            
            # 거래 내역 기록
            Transaction.objects.create(
                portfolio=portfolio,
                transaction_type='SELL',
                stock=stock,
                quantity=quantity,
                price=price,
                amount=total_amount,
                balance_before=balance_before,
                balance_after=balance_after
            )
            
            return {
                'success': True,
                'message': f'{stock.name} {quantity}주 매도 완료',
                'new_balance': balance_after
            }
    
    @staticmethod
    def get_portfolio_summary(user: User) -> dict:
        """포트폴리오 요약 정보"""
        portfolio = PortfolioService.get_or_create_portfolio(user)
        positions = portfolio.positions.all()
        
        # 주식별 상세 정보
        stock_details = []
        total_stock_value = Decimal('0')
        total_unrealized_pnl = Decimal('0')
        
        for position in positions:
            stock_value = position.current_value
            unrealized_pnl = position.unrealized_pnl
            
            stock_details.append({
                'ticker': position.stock.ticker,
                'name': position.stock.name,
                'quantity': position.quantity,
                'average_price': position.average_price,
                'current_price': position.stock.current_price,
                'current_value': stock_value,
                'unrealized_pnl': unrealized_pnl,
                'unrealized_pnl_percent': position.unrealized_pnl_percent,
                'weight': (stock_value / portfolio.total_value * 100) if portfolio.total_value > 0 else 0
            })
            
            total_stock_value += stock_value
            total_unrealized_pnl += unrealized_pnl
        
        return {
            'portfolio': portfolio,
            'total_value': portfolio.total_value,
            'total_return': portfolio.total_return,
            'cash_balance': portfolio.current_balance,
            'cash_ratio': portfolio.cash_ratio,
            'stock_value': total_stock_value,
            'unrealized_pnl': total_unrealized_pnl,
            'positions': stock_details,
            'recent_transactions': portfolio.transactions.all()[:10]
        }
    
    @staticmethod
    def add_to_watchlist(user: User, ticker: str) -> dict:
        """관심종목 추가"""
        stock = Stock.objects.get(ticker=ticker)
        watchlist, created = Watchlist.objects.get_or_create(
            user=user,
            stock=stock
        )
        
        if created:
            return {
                'success': True,
                'message': f'{stock.name}이 관심종목에 추가되었습니다'
            }
        else:
            return {
                'success': False,
                'message': f'{stock.name}은 이미 관심종목에 있습니다'
            }
    
    @staticmethod
    def remove_from_watchlist(user: User, ticker: str) -> dict:
        """관심종목 제거"""
        try:
            watchlist = Watchlist.objects.get(user=user, stock__ticker=ticker)
            stock_name = watchlist.stock.name
            watchlist.delete()
            
            return {
                'success': True,
                'message': f'{stock_name}이 관심종목에서 제거되었습니다'
            }
        except Watchlist.DoesNotExist:
            return {
                'success': False,
                'message': '관심종목에 없는 주식입니다'
            }
    
    @staticmethod
    def get_watchlist(user: User) -> list:
        """관심종목 목록"""
        watchlists = Watchlist.objects.filter(user=user).select_related('stock')
        
        watchlist_data = []
        for watchlist in watchlists:
            stock = watchlist.stock
            watchlist_data.append({
                'ticker': stock.ticker,
                'name': stock.name,
                'current_price': stock.current_price,
                'price_change': stock.price_change,
                'sector': stock.sector,
                'added_at': watchlist.added_at
            })
        
        return watchlist_data


class StockService:
    """주식 관리 서비스"""
    
    @staticmethod
    def get_all_stocks() -> list:
        """모든 주식 정보"""
        stocks = Stock.objects.all()
        
        stock_data = []
        for stock in stocks:
            stock_data.append({
                'ticker': stock.ticker,
                'name': stock.name,
                'sector': stock.sector,
                'current_price': stock.current_price,
                'base_price': stock.base_price,
                'price_change': stock.price_change,
                'updated_at': stock.updated_at
            })
        
        return stock_data
    
    @staticmethod
    def update_stock_price(ticker: str, new_price: Decimal) -> bool:
        """주식 가격 업데이트"""
        try:
            stock = Stock.objects.get(ticker=ticker)
            stock.current_price = new_price
            stock.save()
            return True
        except Stock.DoesNotExist:
            return False
    
    @staticmethod
    def initialize_stocks() -> bool:
        """초기 주식 데이터 생성 - 한국 주식 거래량 상위 25개 종목"""
        initial_stocks = [
            # 반도체/전자
            {'ticker': '005930', 'name': '삼성전자', 'sector': '반도체', 'price': 79000},
            {'ticker': '000660', 'name': 'SK하이닉스', 'sector': '반도체', 'price': 45000},
            {'ticker': '035420', 'name': 'NAVER', 'sector': '인터넷', 'price': 220000},
            {'ticker': '051910', 'name': 'LG화학', 'sector': '화학', 'price': 520000},
            {'ticker': '006400', 'name': '삼성SDI', 'sector': '화학', 'price': 380000},
            
            # 자동차
            {'ticker': '005380', 'name': '현대차', 'sector': '자동차', 'price': 180000},
            {'ticker': '005490', 'name': '기아', 'sector': '자동차', 'price': 85000},
            {'ticker': '012450', 'name': '한화에어로스페이스', 'sector': '방산', 'price': 45000},
            
            # 금융
            {'ticker': '055550', 'name': '신한지주', 'sector': '금융', 'price': 45000},
            {'ticker': '086790', 'name': '하나금융지주', 'sector': '금융', 'price': 42000},
            {'ticker': '105560', 'name': 'KB금융', 'sector': '금융', 'price': 65000},
            {'ticker': '138930', 'name': 'BNK금융지주', 'sector': '금융', 'price': 8500},
            
            # 건설/조선
            {'ticker': '028260', 'name': '삼성물산', 'sector': '건설', 'price': 45000},
            {'ticker': '009540', 'name': '현대중공업', 'sector': '조선', 'price': 120000},
            {'ticker': '010140', 'name': '삼성중공업', 'sector': '조선', 'price': 8500},
            
            # 통신/미디어
            {'ticker': '017670', 'name': 'SK텔레콤', 'sector': '통신', 'price': 52000},
            {'ticker': '030200', 'name': 'KT', 'sector': '통신', 'price': 35000},
            {'ticker': '011070', 'name': 'LG이노텍', 'sector': '전자부품', 'price': 180000},
            
            # 제조/소재
            {'ticker': '015760', 'name': '한국전력', 'sector': '전력', 'price': 22000},
            {'ticker': '096770', 'name': 'SK이노베이션', 'sector': '에너지', 'price': 120000},
            {'ticker': '068270', 'name': '셀트리온', 'sector': '바이오', 'price': 180000},
            {'ticker': '207940', 'name': '삼성바이오로직스', 'sector': '바이오', 'price': 850000},
            
            # 소비재
            {'ticker': '097950', 'name': 'CJ제일제당', 'sector': '식품', 'price': 380000},
            {'ticker': '035720', 'name': '카카오', 'sector': '인터넷', 'price': 45000},
            {'ticker': '323410', 'name': '카카오뱅크', 'sector': '금융', 'price': 28000},
            {'ticker': '373220', 'name': 'LG에너지솔루션', 'sector': '화학', 'price': 450000},
        ]
        
        for stock_data in initial_stocks:
            Stock.objects.get_or_create(
                ticker=stock_data['ticker'],
                defaults={
                    'name': stock_data['name'],
                    'sector': stock_data['sector'],
                    'current_price': stock_data['price'],
                    'base_price': stock_data['price']
                }
            )
        
        return True 