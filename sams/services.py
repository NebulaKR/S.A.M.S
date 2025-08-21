from django.contrib.auth.models import User
from django.db import transaction
from decimal import Decimal
import json
import threading
import time
from datetime import datetime
from .models import Portfolio, Stock, Position, Transaction, Watchlist
from core.models.simulation_engine import SimulationEngine
from data.parameter_templates import get_initial_data
from utils.logger import save_event_log, save_market_snapshot


class PortfolioService:
    @staticmethod
    def get_portfolio_summary(user):
        """사용자의 포트폴리오 요약 정보를 반환합니다."""
        try:
            portfolio = Portfolio.objects.get(user=user)
            positions = portfolio.positions.all()
            
            total_stock_value = sum(position.current_value for position in positions)
            total_value = portfolio.current_balance + total_stock_value
            
            return {
                'total_value': float(total_value),
                'cash_balance': float(portfolio.current_balance),
                'stock_value': float(total_stock_value),
                'total_return': float(portfolio.total_return),
                'cash_ratio': float(portfolio.cash_ratio),
                'positions': []
            }
        except Portfolio.DoesNotExist:
            return {
                'total_value': 0.0,
                'cash_balance': 0.0,
                'stock_value': 0.0,
                'total_return': 0.0,
                'cash_ratio': 100.0,
                'positions': []
            }
    
    @staticmethod
    def buy_stock(user, ticker, quantity, price):
        """주식 매수 처리"""
        try:
            with transaction.atomic():
                stock = Stock.objects.get(ticker=ticker)
                portfolio, created = Portfolio.objects.get_or_create(user=user)
                
                total_cost = price * quantity
                
                if portfolio.current_balance < total_cost:
                    return {'success': False, 'message': '잔액이 부족합니다.'}
                
                # 기존 포지션이 있는지 확인
                position, created = portfolio.positions.get_or_create(
                    stock=stock,
                    defaults={'quantity': 0, 'average_price': Decimal('0')}
                )
                
                if created:
                    # 새로운 포지션
                    position.quantity = quantity
                    position.average_price = price
                else:
                    # 기존 포지션 업데이트
                    total_quantity = position.quantity + quantity
                    total_cost_before = position.average_price * position.quantity
                    total_cost_after = total_cost_before + total_cost
                    position.average_price = total_cost_after / total_quantity
                    position.quantity = total_quantity
                
                position.save()
                portfolio.current_balance -= total_cost
                portfolio.save()
            
            return {
                'success': True,
                'message': f'{stock.name} {quantity}주 매수 완료',
                'total_cost': float(total_cost),
                'remaining_balance': float(portfolio.current_balance)
            }
                
        except Stock.DoesNotExist:
            return {'success': False, 'message': '존재하지 않는 종목입니다.'}
        except Exception as e:
            return {'success': False, 'message': f'매수 처리 중 오류가 발생했습니다: {str(e)}'}
    
    @staticmethod
    def sell_stock(user, ticker, quantity, price):
        """주식 매도 처리"""
        try:
            with transaction.atomic():
                stock = Stock.objects.get(ticker=ticker)
                portfolio = Portfolio.objects.get(user=user)
                
                try:
                    position = portfolio.positions.get(stock=stock)
                except portfolio.positions.model.DoesNotExist:
                    return {'success': False, 'message': '보유하지 않은 종목입니다.'}
                
                if position.quantity < quantity:
                    return {'success': False, 'message': '보유 수량이 부족합니다.'}
                
                total_revenue = price * quantity
                realized_pnl = (price - position.average_price) * quantity
                
                # 포지션 업데이트
                position.quantity -= quantity
                if position.quantity == 0:
                    position.delete()
                else:
                    position.save()
                
                portfolio.current_balance += total_revenue
                portfolio.save()
            
            return {
                'success': True,
                'message': f'{stock.name} {quantity}주 매도 완료',
                'total_revenue': float(total_revenue),
                'realized_pnl': float(realized_pnl),
                'remaining_balance': float(portfolio.current_balance)
            }
                
        except Stock.DoesNotExist:
            return {'success': False, 'message': '존재하지 않는 종목입니다.'}
        except Portfolio.DoesNotExist:
            return {'success': False, 'message': '포트폴리오가 없습니다.'}
        except Exception as e:
            return {'success': False, 'message': f'매도 처리 중 오류가 발생했습니다: {str(e)}'}
    
    @staticmethod
    def get_watchlist(user):
        """사용자의 관심종목 목록을 반환합니다."""
        try:
            watchlist = Watchlist.objects.get(user=user)
            return [{'ticker': item.ticker, 'name': item.name} for item in watchlist.stocks.all()]
        except Watchlist.DoesNotExist:
            return []
    
    @staticmethod
    def add_to_watchlist(user, ticker):
        """관심종목에 추가"""
        try:
            stock = Stock.objects.get(ticker=ticker)
            watchlist, created = Watchlist.objects.get_or_create(user=user)
            watchlist.stocks.add(stock)
            
            return {
                'success': True,
                'message': f'{stock.name}이(가) 관심종목에 추가되었습니다.'
            }
        except Stock.DoesNotExist:
            return {'success': False, 'message': '존재하지 않는 종목입니다.'}
        except Exception as e:
            return {'success': False, 'message': f'관심종목 추가 중 오류가 발생했습니다: {str(e)}'}
    
    @staticmethod
    def remove_from_watchlist(user, ticker):
        """관심종목에서 제거"""
        try:
            stock = Stock.objects.get(ticker=ticker)
            watchlist = Watchlist.objects.get(user=user)
            watchlist.stocks.remove(stock)
            
            return {
                'success': True,
                'message': f'{stock.name}이(가) 관심종목에서 제거되었습니다.'
            }
        except Stock.DoesNotExist:
            return {'success': False, 'message': '존재하지 않는 종목입니다.'}
        except Watchlist.DoesNotExist:
            return {'success': False, 'message': '관심종목이 없습니다.'}
        except Exception as e:
            return {'success': False, 'message': f'관심종목 제거 중 오류가 발생했습니다: {str(e)}'}


class StockService:
    @staticmethod
    def get_all_stocks():
        """모든 주식 정보를 반환합니다."""
        stocks = Stock.objects.all()
        return [{
            'ticker': stock.ticker,
            'name': stock.name,
            'current_price': float(stock.current_price),
            'change': float(stock.current_price - stock.base_price),
            'change_percent': float(stock.price_change)
        } for stock in stocks]


class SimulationService:
    """시뮬레이션 관리 서비스"""
    
    _active_simulations = {}  # 시뮬레이션 인스턴스 관리
    
    @classmethod
    def start_simulation(cls, simulation_id, settings):
        """시뮬레이션 시작"""
        try:
            if simulation_id in cls._active_simulations:
                return {'success': False, 'message': f'시뮬레이션 {simulation_id}가 이미 실행 중입니다.'}
            
            # 시뮬레이션 데이터 초기화
            cls._active_simulations[simulation_id] = {
                'status': 'starting',
                'start_time': datetime.now(),
                'total_events': 0,
                'total_news': 0,
                'last_event_time': None
            }
            
            # 별도 스레드에서 시뮬레이션 실행
            thread = threading.Thread(
                target=cls._run_simulation,
                args=(simulation_id, settings),
                daemon=True
            )
            thread.start()
            
            return {'success': True, 'message': f'시뮬레이션 {simulation_id}가 시작되었습니다.'}
            
        except Exception as e:
            return {'success': False, 'message': f'시뮬레이션 시작 실패: {str(e)}'}
    
    @classmethod
    def stop_simulation(cls, simulation_id):
        """시뮬레이션 정지"""
        try:
            if simulation_id not in cls._active_simulations:
                return {'success': False, 'message': f'시뮬레이션 {simulation_id}가 실행 중이 아닙니다.'}
            
            cls._active_simulations[simulation_id]['status'] = 'stopping'
            return {'success': True, 'message': f'시뮬레이션 {simulation_id} 정지 요청됨'}
            
        except Exception as e:
            return {'success': False, 'message': f'시뮬레이션 정지 실패: {str(e)}'}
    
    @classmethod
    def get_simulation_status(cls, simulation_id):
        """시뮬레이션 상태 조회"""
        if simulation_id not in cls._active_simulations:
            return None
        
        sim_data = cls._active_simulations[simulation_id]
        
        # 경과 시간 계산
        elapsed_time = datetime.now() - sim_data['start_time']
        elapsed_hours = int(elapsed_time.total_seconds() // 3600)
        elapsed_minutes = int((elapsed_time.total_seconds() % 3600) // 60)
        
        return {
            'simulation_id': simulation_id,
            'status': sim_data['status'],
            'start_time': sim_data['start_time'].isoformat(),
            'elapsed_time': f'{elapsed_hours}시간 {elapsed_minutes}분',
            'total_events': sim_data['total_events'],
            'total_news': sim_data['total_news'],
            'last_event_time': sim_data['last_event_time'].isoformat() if sim_data['last_event_time'] else None,
            'performance': {
                'cpu_usage': '45%',  # 실제로는 시스템 모니터링 필요
                'memory_usage': '2.3GB',
                'events_per_minute': sim_data['total_events'] / max(1, elapsed_time.total_seconds() / 60)
            }
        }
    
    @classmethod
    def _run_simulation(cls, simulation_id, settings):
        """시뮬레이션 실행 (별도 스레드)"""
        try:
            # 시뮬레이션 엔진 초기화
            initial_data = get_initial_data()
            
            # 사용자 설정이 있으면 적용
            if 'market_params' in settings:
                initial_data['market_params'] = settings['market_params']
                print(f"=== 시뮬레이션 엔진 초기화 ===")
                print(f"시뮬레이션 ID: {simulation_id}")
                print(f"적용된 시장 파라미터: {json.dumps(settings['market_params'], indent=2, ensure_ascii=False)}")
                print(f"이벤트 생성 간격: {settings.get('event_generation_interval', 30)}초")
                print(f"뉴스 생성 활성화: {settings.get('news_generation_enabled', True)}")
                print(f"최대 이벤트/시간: {settings.get('max_events_per_hour', 10)}")
                print(f"허용 카테고리: {settings.get('allowed_categories', [])}")
            
            engine = SimulationEngine(initial_data)
            engine.enable_news_generation(settings['news_generation_enabled'])
            engine.set_event_generation_interval(settings.get('event_generation_interval', 30))
            engine.set_allowed_categories(settings.get('allowed_categories', ["경제", "정책", "기업", "기술", "국제"]))
            
            # 시뮬레이션 엔진 시작
            engine.start()
            
            # 시뮬레이션 상태 업데이트
            cls._active_simulations[simulation_id]['status'] = 'running'
            
            # 이벤트 생성 콜백
            def on_event_occur(event_data):
                cls._active_simulations[simulation_id]['total_events'] += 1
                cls._active_simulations[simulation_id]['last_event_time'] = datetime.now()
                
                # 이벤트 로그 저장
                save_event_log(
                    sim_id=simulation_id,
                    event_id=event_data['id'],
                    event=event_data,
                    affected_stocks=event_data.get('affected_stocks', []),
                    market_impact=event_data.get('market_impact', 0),
                    simulation_time=datetime.now().isoformat()
                )
            
            # 뉴스 생성 콜백
            def on_news_update(news_data):
                cls._active_simulations[simulation_id]['total_news'] += 1
            
            engine.add_callback("event_occur", on_event_occur)
            engine.add_callback("news_update", on_news_update)
            
            # 시뮬레이션 루프
            while cls._active_simulations[simulation_id]['status'] == 'running':
                engine.update()
                time.sleep(settings['event_generation_interval'])
                
                # 시간당 최대 이벤트 수 체크
                if cls._active_simulations[simulation_id]['total_events'] >= settings['max_events_per_hour']:
                    time.sleep(3600)  # 1시간 대기
                    cls._active_simulations[simulation_id]['total_events'] = 0
            
            # 시뮬레이션 종료
            cls._active_simulations[simulation_id]['status'] = 'stopped'
            
        except Exception as e:
            cls._active_simulations[simulation_id]['status'] = 'error'
            print(f"시뮬레이션 오류 ({simulation_id}): {str(e)}")
    
    @classmethod
    def get_all_simulation_status(cls):
        """모든 시뮬레이션 상태 조회"""
        return {
            sim_id: cls.get_simulation_status(sim_id)
            for sim_id in cls._active_simulations.keys()
        } 