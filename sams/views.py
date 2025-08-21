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

from .services import PortfolioService, StockService, SimulationService
from .models import Stock
from utils.logger import (
    list_event_logs, 
    get_news_articles_for_event, 
    get_event_log,
    get_recent_events_for_context
)

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
def home(request): # 최초 로그인 시에 보이는 화면 수정 필요
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
def news_dashboard(request):
    """뉴스 대시보드"""
    context = {
        'news_active': True,
    }
    return render(request, 'app/news_dashboard.html', context)

@login_required
def admin_dashboard(request):
    """관리자 대시보드"""
    # 관리자 권한 확인 (간단한 예시)
    if not request.user.is_staff:
        return redirect('home')
    
    context = {
        'admin_active': True,
    }
    return render(request, 'app/admin_dashboard.html', context)

# 시뮬레이션 제어 API들
@login_required
def start_simulation(request):
    """시뮬레이션 시작 API"""
    if not request.user.is_staff:
        return JsonResponse({'success': False, 'message': '관리자 권한이 필요합니다.'})
    
    try:
        data = json.loads(request.body) if request.body else {}
        sim_id = data.get('simulation_id', 'default-sim')
        settings = data.get('settings', {})
        
        # 디버깅을 위한 로그 출력
        print(f"=== 시뮬레이션 시작 요청 ===")
        print(f"시뮬레이션 ID: {sim_id}")
        print(f"설정: {json.dumps(settings, indent=2, ensure_ascii=False)}")
        
        # 시뮬레이션 서비스를 통한 시작
        result = SimulationService.start_simulation(sim_id, settings)
        
        print(f"시뮬레이션 시작 결과: {result}")
        return JsonResponse(result)
    except Exception as e:
        print(f"시뮬레이션 시작 오류: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': f'시뮬레이션 시작 실패: {str(e)}'
        })

@login_required
def stop_simulation(request):
    """시뮬레이션 정지 API"""
    if not request.user.is_staff:
        return JsonResponse({'success': False, 'message': '관리자 권한이 필요합니다.'})
    
    try:
        data = json.loads(request.body) if request.body else {}
        sim_id = data.get('simulation_id', 'default-sim')
        
        # 시뮬레이션 서비스를 통한 정지
        result = SimulationService.stop_simulation(sim_id)
        
        return JsonResponse(result)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'시뮬레이션 정지 실패: {str(e)}'
        })

@login_required
def get_simulation_control_status(request):
    """시뮬레이션 제어 상태 조회 API"""
    if not request.user.is_staff:
        return JsonResponse({'success': False, 'message': '관리자 권한이 필요합니다.'})
    
    try:
        sim_id = request.GET.get('simulation_id', 'default-sim')
        
        # 시뮬레이션 서비스에서 상태 조회
        status_data = SimulationService.get_simulation_status(sim_id)
        
        if status_data is None:
            return JsonResponse({
                'success': False,
                'message': '실행 중인 시뮬레이션이 없습니다.'
            })
        
        return JsonResponse({
            'success': True,
            'data': status_data
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'상태 조회 실패: {str(e)}'
        })

@login_required
def get_simulation_logs(request):
    """시뮬레이션 로그 조회 API"""
    if not request.user.is_staff:
        return JsonResponse({'success': False, 'message': '관리자 권한이 필요합니다.'})
    
    try:
        sim_id = request.GET.get('simulation_id', 'default-sim')
        limit = int(request.GET.get('limit', 50))
        
        # 실제로는 시뮬레이션 로그를 조회
        # 여기서는 예시 데이터 반환
        
        logs = [
            {
                'timestamp': '2024-01-15T12:30:00Z',
                'level': 'INFO',
                'message': '새로운 이벤트 생성: AI 칩 수요 폭증',
                'event_id': 'event-123'
            },
            {
                'timestamp': '2024-01-15T12:29:45Z',
                'level': 'INFO',
                'message': '뉴스 기사 생성 완료: 조선일보, 한겨레, 매일경제',
                'event_id': 'event-122'
            },
            {
                'timestamp': '2024-01-15T12:29:30Z',
                'level': 'WARNING',
                'message': 'LLM 응답 지연: 3초',
                'event_id': None
            }
        ]
        
        return JsonResponse({
            'success': True,
            'data': {
                'logs': logs,
                'total_count': len(logs)
            }
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'로그 조회 실패: {str(e)}'
        })

@login_required
def update_simulation_settings(request):
    """시뮬레이션 설정 업데이트 API"""
    if not request.user.is_staff:
        return JsonResponse({'success': False, 'message': '관리자 권한이 필요합니다.'})
    
    try:
        data = json.loads(request.body)
        
        # 설정 업데이트 로직
        settings = {
            'event_generation_interval': data.get('event_generation_interval', 30),
            'news_generation_enabled': data.get('news_generation_enabled', True),
            'max_events_per_hour': data.get('max_events_per_hour', 10),
            'simulation_speed': data.get('simulation_speed', 2),
            'allowed_categories': data.get('allowed_categories', ['경제', '정책', '기업', '기술', '국제']),
            'market_params': data.get('market_params', {})
        }
        
        return JsonResponse({
            'success': True,
            'message': '시뮬레이션 설정이 업데이트되었습니다.',
            'settings': settings
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'설정 업데이트 실패: {str(e)}'
        })

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

# ============================================================================
# 파이어베이스 시뮬레이션 데이터 API 엔드포인트들
# ============================================================================

@login_required
def get_simulation_status(request):
    """시뮬레이션 상태 조회 API"""
    try:
        sim_id = request.GET.get('simulation_id', 'default-sim')
        
        # 최근 이벤트 로그 조회
        recent_events = list_event_logs(sim_id, limit=1)
        
        if not recent_events:
            return JsonResponse({
                'success': True,
                'data': {
                    'simulation_id': sim_id,
                    'status': 'no_data',
                    'message': '시뮬레이션 데이터가 없습니다.'
                }
            })
        
        latest_event = recent_events[0]
        event_data = latest_event.get('event', {})
        
        # 전체 이벤트 수 조회
        all_events = list_event_logs(sim_id, limit=1000)  # 충분히 큰 수로 전체 조회
        
        status_data = {
            'simulation_id': sim_id,
            'status': 'active',
            'latest_event': {
                'id': event_data.get('id'),
                'event_type': event_data.get('event_type'),
                'category': event_data.get('category'),
                'sentiment': event_data.get('sentiment'),
                'impact_level': event_data.get('impact_level'),
                'timestamp': latest_event.get('simulation_time'),
                'created_at': latest_event.get('created_at')
            },
            'total_events': len(all_events),
            'last_updated': latest_event.get('created_at')
        }
        
        return JsonResponse({
            'success': True,
            'data': status_data
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False, 
            'message': f'시뮬레이션 상태 조회 중 오류가 발생했습니다: {str(e)}'
        })

@login_required
def get_recent_events(request):
    """최근 이벤트 목록 조회 API"""
    try:
        sim_id = request.GET.get('simulation_id', 'default-sim')
        limit = int(request.GET.get('limit', 10))
        
        events = list_event_logs(sim_id, limit=limit)
        
        events_data = []
        for event_log in events:
            event = event_log.get('event', {})
            events_data.append({
                'id': event.get('id'),
                'event_type': event.get('event_type'),
                'category': event.get('category'),
                'sentiment': event.get('sentiment'),
                'impact_level': event.get('impact_level'),
                'duration': event.get('duration'),
                'affected_stocks': event_log.get('affected_stocks', []),
                'market_impact': event_log.get('market_impact', 0),
                'simulation_time': event_log.get('simulation_time'),
                'created_at': event_log.get('created_at'),
                'market_context': event.get('market_context', {})
            })
        
        return JsonResponse({
            'success': True,
            'data': {
                'events': events_data,
                'total_count': len(events_data)
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False, 
            'message': f'이벤트 목록 조회 중 오류가 발생했습니다: {str(e)}'
        })

@login_required
def get_event_detail(request):
    """특정 이벤트 상세 정보 조회 API"""
    try:
        sim_id = request.GET.get('simulation_id', 'default-sim')
        event_id = request.GET.get('event_id')
        
        if not event_id:
            return JsonResponse({
                'success': False, 
                'message': '이벤트 ID가 필요합니다.'
            })
        
        event_log = get_event_log(sim_id, event_id)
        
        if not event_log:
            return JsonResponse({
                'success': False, 
                'message': '이벤트를 찾을 수 없습니다.'
            })
        
        event = event_log.get('event', {})
        
        # 해당 이벤트의 뉴스 기사들 조회
        news_articles = get_news_articles_for_event(sim_id, event_id)
        
        event_detail = {
            'id': event.get('id'),
            'event_type': event.get('event_type'),
            'category': event.get('category'),
            'sentiment': event.get('sentiment'),
            'impact_level': event.get('impact_level'),
            'duration': event.get('duration'),
            'affected_stocks': event_log.get('affected_stocks', []),
            'market_impact': event_log.get('market_impact', 0),
            'simulation_time': event_log.get('simulation_time'),
            'created_at': event_log.get('created_at'),
            'market_context': event.get('market_context', {}),
            'news_articles': news_articles
        }
        
        return JsonResponse({
            'success': True,
            'data': event_detail
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False, 
            'message': f'이벤트 상세 조회 중 오류가 발생했습니다: {str(e)}'
        })

@login_required
def get_news_feed(request):
    """뉴스 피드 조회 API"""
    try:
        sim_id = request.GET.get('simulation_id', 'default-sim')
        limit = int(request.GET.get('limit', 20))
        media_filter = request.GET.get('media')  # 특정 언론사 필터
        
        # 최근 이벤트들 조회
        recent_events = list_event_logs(sim_id, limit=limit)
        
        news_feed = []
        for event_log in recent_events:
            event = event_log.get('event', {})
            event_id = event.get('id')
            
            # 해당 이벤트의 뉴스 기사들 조회
            news_articles = get_news_articles_for_event(sim_id, event_id)
            
            # 언론사 필터 적용
            if media_filter:
                news_articles = [news for news in news_articles 
                               if news.get('media_name') == media_filter]
            
            for news in news_articles:
                news_feed.append({
                    'news_id': news.get('news_id'),
                    'media_name': news.get('media_name'),
                    'article_text': news.get('article_text'),
                    'created_at': news.get('created_at'),
                    'outlet_bias': news.get('meta', {}).get('outlet_bias'),
                    'outlet_credibility': news.get('meta', {}).get('outlet_credibility'),
                    'event_info': {
                        'event_id': event_id,
                        'event_type': event.get('event_type'),
                        'category': event.get('category'),
                        'sentiment': event.get('sentiment'),
                        'impact_level': event.get('impact_level')
                    }
                })
        
        # 생성 시간 기준으로 정렬 (최신순)
        news_feed.sort(key=lambda x: x['created_at'], reverse=True)
        
        return JsonResponse({
            'success': True,
            'data': {
                'news_feed': news_feed,
                'total_count': len(news_feed)
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False, 
            'message': f'뉴스 피드 조회 중 오류가 발생했습니다: {str(e)}'
        })

@login_required
def get_market_summary(request):
    """시장 요약 정보 조회 API"""
    try:
        sim_id = request.GET.get('simulation_id', 'default-sim')
        
        # 최근 이벤트들 조회
        recent_events = list_event_logs(sim_id, limit=50)
        
        if not recent_events:
            return JsonResponse({
                'success': True,
                'data': {
                    'message': '시장 데이터가 없습니다.'
                }
            })
        
        # 카테고리별 이벤트 통계
        category_stats = {}
        sentiment_sum = 0
        impact_sum = 0
        
        for event_log in recent_events:
            event = event_log.get('event', {})
            category = event.get('category', '기타')
            sentiment = event.get('sentiment', 0)
            impact = event.get('impact_level', 3)
            
            if category not in category_stats:
                category_stats[category] = 0
            category_stats[category] += 1
            
            sentiment_sum += sentiment
            impact_sum += impact
        
        avg_sentiment = sentiment_sum / len(recent_events) if recent_events else 0
        avg_impact = impact_sum / len(recent_events) if recent_events else 0
        
        # 최근 시장 상태 정보 (가장 최근 이벤트의 market_context에서 추출)
        latest_event = recent_events[0]
        market_context = latest_event.get('event', {}).get('market_context', {})
        market_state = market_context.get('market_state', {})
        
        market_summary = {
            'total_events': len(recent_events),
            'category_distribution': category_stats,
            'average_sentiment': avg_sentiment,
            'average_impact': avg_impact,
            'market_sentiment': market_state.get('market_sentiment', 'neutral'),
            'average_change_rate': market_state.get('average_change_rate', 0),
            'market_volatility': market_context.get('market_volatility', 0),
            'last_updated': latest_event.get('created_at')
        }
        
        return JsonResponse({
            'success': True,
            'data': market_summary
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False, 
            'message': f'시장 요약 조회 중 오류가 발생했습니다: {str(e)}'
        })

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
