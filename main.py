from core.models.announcer.announcer import Announcer
from core.models.announcer.event import Event
from core.models.announcer.news import Media
from core.models.config.generator import get_internal_params, build_entities_from_params
from core.models.coach.coach import Coach
from core.models.main_model import main_model
from core.models.simulation_engine import SimulationEngine, SimulationSpeed
from utils.id_generator import generate_id
from utils.logger import save_event_log, save_news_article
from datetime import datetime
import time

if __name__ == "__main__":
	# 시뮬레이션 ID 생성
	sim_id = generate_id("sim")
	print(f"시뮬레이션 ID: {sim_id}")
	
	# 과거 사건 (있으면 전달)
	past_events: list[Event] = []

	# 1) 사건 N개 생성
	announcer = Announcer()
	new_events = announcer.generate_events(
		past_events=past_events,
		count=2,
		allowed_categories=["Tech", "Healthcare", "Policy"]
	)

	# 2) 언론사 목록
	outlets = [
		Media(name="뉴스24", bias=0.2, credibility=0.9),
		Media(name="SNS속보", bias=0.8, credibility=0.3),
	]

	# 내부 파라미터 생성 및 엔티티 변환 → 코치 가중치 산출
	raw_params = get_internal_params(seed=7)
	entity_params = build_entities_from_params(raw_params)
	coach = Coach(entity_params)
	weights = coach.adjust_weights()

	# 3) 시뮬레이션 엔진 초기화
	# entity_params를 딕셔너리로 변환
	market_params_dict = {
		"public": {
			"consumer_index": entity_params["public"].consumer_index,
			"risk_appetite": entity_params["public"].risk_appetite,
			"news_sensitivity": entity_params["public"].news_sensitivity,
		},
		"company": {
			"industry": entity_params["company"].industry,
			"orientation": entity_params["company"].orientation,
			"size": entity_params["company"].size,
			"rnd_focus": entity_params["company"].rnd_focus,
			"volatility": entity_params["company"].volatility,
		},
		"government": {
			"policy_direction": entity_params["government"].policy_direction,
			"interest_rate": entity_params["government"].interest_rate,
			"tax_policy": entity_params["government"].tax_policy,
			"industry_support": entity_params["government"].industry_support,
		},
		"news": {
			"bias": entity_params["news"].bias,
			"credibility": entity_params["news"].credibility,
			"impact_level": entity_params["news"].impact_level,
			"category": entity_params["news"].category,
			"sentiment": entity_params["news"].sentiment,
		}
	}
	
	initial_data = {
		"stocks": {
			"005930": {"price": 79000, "volume": 1000000, "base_price": 79000},  # 삼성전자
			"000660": {"price": 45000, "volume": 500000, "base_price": 45000},   # SK하이닉스
			"051910": {"price": 120000, "volume": 300000, "base_price": 120000}, # LG화학
		},
		"market_params": market_params_dict
	}
	
	engine = SimulationEngine(initial_data)
	engine.set_speed(SimulationSpeed.FAST)  # 빠른 속도로 설정
	engine.set_event_generation_interval(5)  # 5초마다 이벤트 생성
	
	# 콜백 함수 등록
	def on_price_change(stock_price):
		print(f"📈 주가 변동: {stock_price.ticker} {stock_price.base_price:.0f} → {stock_price.current_price:.0f} ({stock_price.change_rate:+.2%})")
	
	def on_event_occur(event_data):
		print(f"🎯 이벤트 발생: {event_data.event.event_type}")
	
	def on_news_update(news_data):
		print(f"📰 뉴스 생성: {news_data.media}")
	
	engine.on_price_change = on_price_change
	engine.on_event_occur = on_event_occur
	engine.on_news_update = on_news_update
	
	# 4) 각 사건에 대해 뉴스 생성 및 메인 모델 계산
	for ev in new_events:
		# 이벤트를 Firebase에 저장
		event_id = ev.id
		save_event_log(
			sim_id=sim_id,
			event_id=event_id,
			event_payload={
				"event_type": ev.event_type,
				"category": ev.category,
				"sentiment": ev.sentiment,
				"impact_level": ev.impact_level,
				"duration": ev.duration
			},
			affected_stocks=["005930", "000660"],  # 모든 주식에 영향
			market_impact=ev.impact_level / 5.0,
			simulation_time=datetime.now()
		)
		
		# Firebase 기반 뉴스 생성 (DB에 저장됨)
		news_list = announcer.generate_news_for_event_from_firestore(
			sim_id=sim_id,
			event_id=event_id,
			outlets=outlets,
			context_events_limit=5
		)
		
		# Event 객체의 news_article 리스트 업데이트
		for news in news_list:
			ev.news_article.append(news.id)
		
		print("\n생성된 사건:", ev.event_type, "/", ev.category, "/", ev.duration)
		print("연결된 뉴스 ID:", ev.news_article)
		for n in news_list:
			print(f"\n언론사: {n.media}\n{n.article_text}")

		# 과거 목록에 이번 사건 추가 (다음 라운드 맥락 강화를 위해)
		past_events.append(ev)

		# 뉴스 임팩트 간단 추정: sentiment(-1~1)→[0,1] 변환 후 impact_level(1~5) 가중
		sentiment_score = max(0.0, min(1.0, (ev.sentiment + 1.0) / 2.0))
		impact_scale = max(0.0, min(1.0, ev.impact_level / 5.0))
		base_news_impact = round(sentiment_score * impact_scale, 3)

		# 미디어 신뢰도 보정 (평균 credibility)
		avg_cred = sum(o.credibility for o in outlets) / max(1, len(outlets))

		# 메인 모델 계산 (엔티티 파라미터 사용)
		result = main_model(weights, entity_params, {
			"news_impact": base_news_impact,
			"media_credibility": avg_cred,
		}, base_price=100.0)

		print("\n🧮 메인 모델 계산:")
		print(f"- 가중치: {weights}")
		print(f"- 추정 news_impact: {base_news_impact} (cred x{avg_cred:.2f})")
		print(f"- delta: {result['delta']}, price: {result['price']}")
	
	# 5) 시뮬레이션 엔진 시작하여 주가 변동 시뮬레이션
	print("\n🚀 시뮬레이션 엔진 시작 - 주가 변동 시뮬레이션")
	engine.start()
	
	# 시뮬레이션 루프 실행 (10초간)
	start_time = time.time()
	while time.time() - start_time < 10:
		engine.update()
		time.sleep(0.5)  # 0.5초마다 업데이트
	
	# 최종 상태 출력
	final_state = engine.get_current_state()
	print(f"\n📊 최종 시뮬레이션 상태:")
	print(f"- 시뮬레이션 시간: {final_state['simulation_time']}")
	print(f"- 생성된 이벤트 수: {len(final_state['recent_events'])}")
	print(f"- 현재 주가:")
	for ticker, stock_data in final_state['stocks'].items():
		base_price = stock_data.get('base_price', stock_data['price'])
		current_price = stock_data['price']
		change_rate = stock_data.get('change_rate', 0.0)
		print(f"  {ticker}: {base_price:.0f} → {current_price:.0f} ({change_rate:+.2%})")
	
	engine.stop()
	print("✅ 시뮬레이션 완료!")
