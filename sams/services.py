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
            positions = portfolio.positions.all().select_related('stock')
            
            total_stock_value = sum(position.current_value for position in positions)
            total_value = portfolio.current_balance + total_stock_value
            
            # 포지션 정보 포함
            positions_data = [{
                'ticker': position.stock.ticker,
                'name': position.stock.name,
                'quantity': position.quantity,
                'average_price': float(position.average_price),
                'current_price': float(position.stock.current_price),
                'current_value': float(position.current_value),
                'unrealized_pnl': float(position.unrealized_pnl),
                'unrealized_pnl_percent': float(position.unrealized_pnl_percent),
                'weight': float((position.current_value / total_value * 100) if total_value > 0 else 0)
            } for position in positions]
            
            return {
                'total_value': float(total_value),
                'cash_balance': float(portfolio.current_balance),
                'stock_value': float(total_stock_value),
                'total_return': float(portfolio.total_return),
                'cash_ratio': float(portfolio.cash_ratio),
                'positions': positions_data
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
                balance_before = portfolio.current_balance
                
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
                
                # 거래 내역 저장
                from .models import Transaction
                Transaction.objects.create(
                    portfolio=portfolio,
                    transaction_type='BUY',
                    stock=stock,
                    quantity=quantity,
                    price=price,
                    amount=total_cost,
                    balance_before=balance_before,
                    balance_after=portfolio.current_balance
                )
            
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
                balance_before = portfolio.current_balance
                
                # 포지션 업데이트
                position.quantity -= quantity
                if position.quantity == 0:
                    position.delete()
                else:
                    position.save()
                
                portfolio.current_balance += total_revenue
                portfolio.save()
                
                # 거래 내역 저장
                from .models import Transaction
                Transaction.objects.create(
                    portfolio=portfolio,
                    transaction_type='SELL',
                    stock=stock,
                    quantity=quantity,
                    price=price,
                    amount=total_revenue,
                    balance_before=balance_before,
                    balance_after=portfolio.current_balance
                )
            
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
            watchlist_items = Watchlist.objects.filter(user=user).select_related('stock')
            return [{
                'ticker': item.stock.ticker,
                'name': item.stock.name,
                'current_price': float(item.stock.current_price),
                'change_percent': float(item.stock.price_change),
                'added_at': item.added_at
            } for item in watchlist_items]
        except Exception as e:
            print(f"관심종목 조회 오류: {str(e)}")
            return []
    
    @staticmethod
    def add_to_watchlist(user, ticker):
        """관심종목에 추가"""
        try:
            stock = Stock.objects.get(ticker=ticker)
            # 이미 관심종목에 있는지 확인
            if Watchlist.objects.filter(user=user, stock=stock).exists():
                return {
                    'success': False,
                    'message': f'{stock.name}은(는) 이미 관심종목에 있습니다.'
                }
            
            # 관심종목에 추가
            Watchlist.objects.create(user=user, stock=stock)
            
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
            watchlist_item = Watchlist.objects.get(user=user, stock=stock)
            watchlist_item.delete()
            
            return {
                'success': True,
                'message': f'{stock.name}이(가) 관심종목에서 제거되었습니다.'
            }
        except Stock.DoesNotExist:
            return {'success': False, 'message': '존재하지 않는 종목입니다.'}
        except Watchlist.DoesNotExist:
            return {'success': False, 'message': '관심종목에 없는 종목입니다.'}
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
            'change_percent': float(stock.price_change),
            'sector': StockService.get_stock_sector(stock.ticker)
        } for stock in stocks]
    
    @staticmethod
    def get_stock_sector(ticker):
        """주식의 섹터를 반환합니다."""
        sector_mapping = {
            # 반도체/전자
            "005930": "반도체",  # 삼성전자
            "000660": "반도체",  # SK하이닉스
            "011070": "반도체",  # LG이노텍
            
            # 자동차/조선
            "005380": "자동차",  # 현대차
            "005490": "자동차",  # 기아
            "009540": "건설",    # 현대중공업
            "010140": "건설",    # 삼성중공업
            "012450": "건설",    # 한화에어로스페이스
            
            # 화학/에너지
            "051910": "화학",    # LG화학
            "006400": "화학",    # 삼성SDI
            "373220": "화학",    # LG에너지솔루션
            "096770": "화학",    # SK이노베이션
            "015760": "화학",    # 한국전력
            
            # 금융
            "055550": "금융",    # 신한지주
            "086790": "금융",    # 하나금융지주
            "105560": "금융",    # KB금융
            "138930": "금융",    # BNK금융지주
            "323410": "금융",    # 카카오뱅크
            
            # 건설
            "028260": "건설",    # 삼성물산
            
            # 통신
            "017670": "통신",    # SK텔레콤
            "030200": "통신",    # KT
            
            # 바이오
            "068270": "바이오",  # 셀트리온
            "207940": "바이오",  # 삼성바이오로직스
            
            # 인터넷
            "035420": "인터넷",  # NAVER
            "035720": "인터넷",  # 카카오
            
            # 식품/소비재
            "097950": "식품",    # CJ제일제당
        }
        return sector_mapping.get(ticker, "기타")
    
    @staticmethod
    def get_all_stocks_with_watchlist_status(user):
        """모든 주식 정보와 관심종목 상태를 반환합니다."""
        stocks = Stock.objects.all()
        user_watchlist = set(Watchlist.objects.filter(user=user).values_list('stock__ticker', flat=True))
        
        return [{
            'ticker': stock.ticker,
            'name': stock.name,
            'current_price': float(stock.current_price),
            'change': float(stock.current_price - stock.base_price),
            'change_percent': float(stock.price_change),
            'sector': StockService.get_stock_sector(stock.ticker),
            'in_watchlist': stock.ticker in user_watchlist
        } for stock in stocks]


class SimulationService:
    """시뮬레이션 관리 서비스"""
    
    _active_simulations = {}  # 시뮬레이션 인스턴스 관리
    
    @classmethod
    def start_simulation(cls, simulation_id, settings):
        """시뮬레이션 시작"""
        try:
            # 기존 시뮬레이션이 실행 중인지 확인
            if simulation_id in cls._active_simulations:
                current_status = cls._active_simulations[simulation_id]['status']
                if current_status in ['running', 'starting']:
                    return {'success': False, 'message': f'시뮬레이션 {simulation_id}가 이미 실행 중입니다.'}
                elif current_status == 'paused':
                    # 일시정지된 상태라면 재개
                    cls._active_simulations[simulation_id]['status'] = 'running'
                    return {'success': True, 'message': f'시뮬레이션 {simulation_id}가 재개되었습니다.'}
                elif current_status in ['stopped', 'error']:
                    # 정지된 상태라면 기존 데이터 정리 후 새로 시작
                    del cls._active_simulations[simulation_id]
            
            # 시뮬레이션 데이터 초기화
            cls._active_simulations[simulation_id] = {
                'status': 'starting',
                'start_time': datetime.now(),
                'total_events': 0,
                'total_news': 0,
                'last_event_time': None,
                'thread': None,
                'engine': None
            }
            
            # 별도 스레드에서 시뮬레이션 실행
            thread = threading.Thread(
                target=cls._run_simulation,
                args=(simulation_id, settings),
                daemon=True
            )
            thread.start()
            
            # 스레드 참조 저장
            cls._active_simulations[simulation_id]['thread'] = thread
            
            return {'success': True, 'message': f'시뮬레이션 {simulation_id}가 시작되었습니다.'}
            
        except Exception as e:
            return {'success': False, 'message': f'시뮬레이션 시작 실패: {str(e)}'}
    
    @classmethod
    def pause_simulation(cls, simulation_id):
        """시뮬레이션 일시정지"""
        try:
            if simulation_id not in cls._active_simulations:
                return {'success': False, 'message': f'시뮬레이션 {simulation_id}가 실행 중이 아닙니다.'}
            
            current_status = cls._active_simulations[simulation_id]['status']
            if current_status == 'running':
                cls._active_simulations[simulation_id]['status'] = 'paused'
                return {'success': True, 'message': f'시뮬레이션 {simulation_id}가 일시정지되었습니다.'}
            elif current_status == 'paused':
                return {'success': False, 'message': f'시뮬레이션 {simulation_id}가 이미 일시정지 상태입니다.'}
            else:
                return {'success': False, 'message': f'시뮬레이션 {simulation_id}가 실행 중이 아닙니다.'}
            
        except Exception as e:
            return {'success': False, 'message': f'시뮬레이션 일시정지 실패: {str(e)}'}

    @classmethod
    def stop_simulation(cls, simulation_id):
        """시뮬레이션 정지"""
        try:
            if simulation_id not in cls._active_simulations:
                return {'success': False, 'message': f'시뮬레이션 {simulation_id}가 실행 중이 아닙니다.'}
            
            current_status = cls._active_simulations[simulation_id]['status']
            if current_status in ['running', 'paused', 'starting']:
                cls._active_simulations[simulation_id]['status'] = 'stopping'
                
                # 시뮬레이션 엔진 정지
                if cls._active_simulations[simulation_id].get('engine'):
                    try:
                        cls._active_simulations[simulation_id]['engine'].stop()
                    except:
                        pass
                
                return {'success': True, 'message': f'시뮬레이션 {simulation_id} 정지 요청됨'}
            else:
                return {'success': False, 'message': f'시뮬레이션 {simulation_id}가 실행 중이 아닙니다.'}
            
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
            print(f"시뮬레이션 루프 시작 - 이벤트 간격: {settings.get('event_generation_interval', 30)}초")
            
            # 엔진 참조 저장
            cls._active_simulations[simulation_id]['engine'] = engine
            
            while cls._active_simulations[simulation_id]['status'] in ['running', 'paused']:
                current_status = cls._active_simulations[simulation_id]['status']
                
                if current_status == 'running':
                    engine.update()
                    
                    # 이벤트 생성 간격을 더 짧게 설정 (테스트용)
                    sleep_interval = min(settings.get('event_generation_interval', 30), 10)  # 최대 10초
                    print(f"시뮬레이션 업데이트 완료, {sleep_interval}초 대기...")
                    
                    # 대기 중에도 상태 변경 확인
                    for i in range(sleep_interval):
                        if cls._active_simulations[simulation_id]['status'] not in ['running', 'paused']:
                            break
                        time.sleep(1)
                    
                    # 시간당 최대 이벤트 수 체크
                    if cls._active_simulations[simulation_id]['total_events'] >= settings.get('max_events_per_hour', 10):
                        print(f"시간당 최대 이벤트 수 도달 ({settings.get('max_events_per_hour', 10)}개), 1시간 대기")
                        time.sleep(3600)  # 1시간 대기
                        cls._active_simulations[simulation_id]['total_events'] = 0
                
                elif current_status == 'paused':
                    print("시뮬레이션 일시정지 중...")
                    time.sleep(1)  # 1초마다 상태 확인
                    continue
                
                # 정지 요청 확인
                if cls._active_simulations[simulation_id]['status'] == 'stopping':
                    break
            
            # 시뮬레이션 종료
            final_status = 'stopped' if cls._active_simulations[simulation_id]['status'] == 'stopping' else 'error'
            cls._active_simulations[simulation_id]['status'] = final_status
            print(f"시뮬레이션 {simulation_id} 종료 - 상태: {final_status}")
            
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