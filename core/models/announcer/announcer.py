import json
import re
import random
from typing import List, Optional

from core.models.announcer.event import Event
from core.models.announcer.news import News, Media
from core.models.announcer.prompt_builder import build_event_prompt
from utils.id_generator import generate_id
from utils.logger import get_event_log, get_recent_events_for_context, save_news_article
from llama_client import query_llm  # Ollama/로컬 LLM HTTP 클라이언트 (이미 사용 중)

class Announcer:
    # -----------------------------
    # 사건 생성: LLM → JSON → Event[]
    # -----------------------------
    def generate_events(
        self,
        past_events: Optional[List[Event]] = None,
        count: int = 1,
        allowed_categories: Optional[List[str]] = None,
        market_context: Optional[dict] = None
    ) -> List[Event]:
        """
        LLM을 사용해 사건 N개를 생성하여 Event 인스턴스 리스트로 반환합니다.
        - past_events: 맥락에 쓰일 과거 사건들
        - count: 생성할 사건 개수
        - allowed_categories: 허용 카테고리 목록
        - market_context: 현재 시장 상태 정보
        """
        # 시장 컨텍스트 정보를 프롬프트에 포함
        context_info = ""
        if market_context:
            market_state = market_context.get("market_state", {})
            market_params = market_context.get("market_params", {})
            
            context_info = f"""
현재 시장 상황:
- 시뮬레이션 시간: {market_context.get('simulation_time', 'N/A')}
- 시장 분위기: {market_state.get('market_sentiment', 'neutral')}
- 평균 변화율: {market_state.get('average_change_rate', 0):.2%}
- 시장 변동성: {market_context.get('market_volatility', 0):.3f}
- 활성 종목 수: {market_state.get('active_stocks_count', 0)}개
- 총 거래량: {market_state.get('total_volume', 0):,}주

시장 파라미터:
- 공공 투자자 위험 선호도: {market_params.get('public', {}).get('risk_appetite', 0):.2f}
- 뉴스 민감도: {market_params.get('public', {}).get('news_sensitivity', 0):.2f}
- 정부 정책 방향: {market_params.get('government', {}).get('policy_direction', 0):.2f}
- 기업 R&D 집중도: {market_params.get('company', {}).get('rnd_focus', 0):.2f}

지금까지 생성된 이벤트 수: {market_context.get('total_events_generated', 0)}개
"""
        
        prompt = build_event_prompt(
            past_events=past_events,
            count=count,
            allowed_categories=allowed_categories,
            language="ko",
            market_context=context_info  # 시장 컨텍스트 정보 전달
        )
        
        # LLM 호출 시도 → 실패 시 합성 이벤트 생성으로 폴백
        data = None
        try:
            raw = query_llm(prompt).strip()
            json_str = self._extract_json_block(raw)
            try:
                data = json.loads(json_str)
            except Exception as e:
                try:
                    data = [json.loads(json_str)]
                except Exception:
                    data = None
        except Exception:
            data = None
        
        if data is None:
            return self._generate_synthetic_events(count=count, allowed_categories=allowed_categories)
        
        if not isinstance(data, list):
            data = [data]
        
        events: List[Event] = []
        for obj in data[:count]:
            item = self._coerce_event_dict(obj)
            ev = Event(
                id=generate_id("event"),
                event_type=item["event_type"],
                category=item["category"],
                sentiment=item["sentiment"],
                impact_level=item["impact_level"],
                duration=item["duration"],
                news_article=[],  # 최초엔 비어 있음
            )
            events.append(ev)
        return events

    # -----------------------------
    # 파이어스토어 기반 뉴스 생성
    # -----------------------------
    def generate_news_for_event_from_firestore(
        self,
        sim_id: str,
        event_id: str,
        outlets: List[Media],
        context_events_limit: int = 5
    ) -> List[News]:
        """
        파이어스토어에서 이벤트 로그를 조회하여 뉴스 기사를 생성합니다.
        
        Args:
            sim_id: 시뮬레이션 ID
            event_id: 이벤트 ID
            outlets: 언론사 목록
            context_events_limit: 컨텍스트로 사용할 최근 이벤트 수
        
        Returns:
            생성된 뉴스 기사 목록
        """
        # 1. 이벤트 로그 조회
        event_log = get_event_log(sim_id, event_id)
        if not event_log:
            print(f"이벤트 로그를 찾을 수 없습니다: {sim_id}/{event_id}")
            return []
        
        # 2. 컨텍스트용 최근 이벤트들 조회
        recent_events = get_recent_events_for_context(sim_id, context_events_limit)
        
        # 3. 각 언론사별로 뉴스 기사 생성
        news_list: List[News] = []
        for outlet in outlets:
            try:
                article_text = self.generate_news_from_event_log(
                    event_log=event_log,
                    outlet=outlet,
                    recent_events=recent_events
                )
            except Exception:
                # LLM 실패 시 합성 기사 텍스트로 폴백
                article_text = self._build_synthetic_article(
                    current_event=event_log.get("event", {}),
                    outlet=outlet,
                    recent_events=recent_events
                )
            
            news_id = generate_id("news")
            news = News(id=news_id, media=outlet.name, article_text=article_text)
            news_list.append(news)
            
            # 4. 생성된 뉴스 기사를 파이어스토어에 저장
            try:
                save_news_article(
                    sim_id=sim_id,
                    event_id=event_id,
                    news_id=news_id,
                    media_name=outlet.name,
                    article_text=article_text,
                    meta={
                        "outlet_bias": outlet.bias,
                        "outlet_credibility": outlet.credibility,
                        "generation_method": "firestore_based_with_fallback"
                    }
                )
            except Exception as e:
                print(f"뉴스 저장 실패: {e}")
            
            print(f"뉴스 기사 생성 완료: {outlet.name} - {news_id}")
        
        return news_list

    def generate_news_from_event_log(
        self,
        event_log: dict,
        outlet: Media,
        recent_events: List[dict]
    ) -> str:
        """
        이벤트 로그를 바탕으로 뉴스 기사를 생성합니다.
        
        Args:
            event_log: 파이어스토어에서 조회한 이벤트 로그
            outlet: 언론사 정보
            recent_events: 최근 이벤트들 (컨텍스트용)
        
        Returns:
            생성된 뉴스 기사 텍스트
        """
        # 1) 프롬프트 구성
        lines = ["다음은 지금까지 발생한 사건들의 요약입니다:\n"]
        
        if recent_events:
            for i, event_data in enumerate(recent_events[-5:], 1):
                event = event_data.get("event", {})
                lines.append(
                    f"{i}. 사건명: {event.get('event_type', 'N/A')} / "
                    f"카테고리: {event.get('category', 'N/A')} / "
                    f"감성: {event.get('sentiment', 0)} / "
                    f"영향: {event.get('impact_level', 3)}"
                )
        else:
            lines.append("이전 사건은 없습니다.")

        # 현재 이벤트 정보
        current_event = event_log.get("event", {})
        lines += [
            "\n현재 사건은 다음과 같습니다:\n",
            "[사건 정보]",
            f"- 제목: {current_event.get('event_type', 'N/A')}",
            f"- 카테고리: {current_event.get('category', 'N/A')}",
            f"- 감성 점수: {current_event.get('sentiment', 0)}",
            f"- 영향 수준: {current_event.get('impact_level', 3)}",
            "",
            "이 사건에 대해, 아래 언론사의 성향과 신뢰도를 반영한 뉴스 기사를 생성하세요:",
            "",
            "[언론사 정보]",
            f"- 이름: {outlet.name}",
            f"- 성향 (bias): {outlet.bias} (-1: 보수, 0: 중립, +1: 진보)",
            f"- 신뢰도 (credibility): {outlet.credibility} (0~1)",
            "",
            "[출력 형식]",
            "뉴스 기사 본문만 출력하세요. 머리말(예: '뉴스 기사:'), 코드블록, 따옴표, 이모지 등은 넣지 마세요.",
            "기사 길이는 250~400자 내외, 한국어로 자연스럽게 작성하세요.",
        ]
        prompt = "\n".join(lines)

        # 2) LLM 호출 (실패 시 상위에서 폴백 처리)
        raw = query_llm(prompt).strip()

        # 3) 후처리: 모델이 JSON/라벨/코드펜스를 섞어 줄 가능성 방지
        text = self._extract_news_text(raw)
        text = self._cleanup_text(text)

        return text

    def generate_news_for_multiple_events(
        self,
        sim_id: str,
        event_ids: List[str],
        outlets: List[Media],
        context_events_limit: int = 5
    ) -> dict:
        """
        여러 이벤트에 대해 일괄적으로 뉴스 기사를 생성합니다.
        
        Args:
            sim_id: 시뮬레이션 ID
            event_ids: 이벤트 ID 목록
            outlets: 언론사 목록
            context_events_limit: 컨텍스트용 최근 이벤트 수
        
        Returns:
            이벤트별 뉴스 기사 목록
        """
        results = {}
        
        for event_id in event_ids:
            try:
                news_list = self.generate_news_for_event_from_firestore(
                    sim_id=sim_id,
                    event_id=event_id,
                    outlets=outlets,
                    context_events_limit=context_events_limit
                )
                results[event_id] = news_list
                print(f"이벤트 {event_id}에 대한 뉴스 기사 {len(news_list)}개 생성 완료")
            except Exception as e:
                print(f"이벤트 {event_id} 뉴스 생성 실패: {e}")
                results[event_id] = []
        
        return results

    # -----------------------------
    # 기존 메서드들 (유지)
    # -----------------------------
    @staticmethod
    def _extract_json_block(text: str) -> str:
        """
        응답에서 JSON 배열 또는 오브젝트 블록만 추출.
        """
        # 배열 우선 탐색
        m_arr = re.search(r"\[\s*\{[\s\S]*?\}\s*\]", text)
        if m_arr:
            return m_arr.group(0)

        # 단일 오브젝트도 지원
        m_obj = re.search(r"\{[\s\S]*\}", text)
        if m_obj:
            return m_obj.group(0)

        raise ValueError(f"JSON 블록을 찾지 못했습니다:\n{text}")

    @staticmethod
    def _coerce_event_dict(obj: dict) -> dict:
        """
        LLM이 반환한 dict을 Event 필드 스펙에 맞게 강제 정리/보정.
        - 값 범위 강제
        - duration 값 표준화
        """
        # 필드 존재 체크 & 기본값
        event_type = str(obj.get("event_type", "이름 미정")).strip()
        category = str(obj.get("category", "기타")).strip()

        # sentiment: float in [-1, 1]
        try:
            sentiment = float(str(obj.get("sentiment", 0)).replace("+", ""))
        except Exception:
            sentiment = 0.0
        sentiment = max(-1.0, min(1.0, sentiment))

        # impact_level: int in [1, 5]
        try:
            impact_level = int(float(obj.get("impact_level", 3)))
        except Exception:
            impact_level = 3
        impact_level = max(1, min(5, impact_level))

        # duration: short/mid/long
        duration_raw = str(obj.get("duration", "mid")).lower().strip()
        if duration_raw in ("s", "short_term", "short"):
            duration = "short"
        elif duration_raw in ("m", "mid_term", "medium", "mid"):
            duration = "mid"
        elif duration_raw in ("l", "long_term", "long"):
            duration = "long"
        else:
            duration = "mid"

        return {
            "event_type": event_type,
            "category": category,
            "sentiment": sentiment,
            "impact_level": impact_level,
            "duration": duration,
        }

    def generate_news_for_event(
        self,
        event: Event,
        outlets: List[Media],
        past_events: Optional[List[Event]] = None
    ) -> List[News]:
        news_list: List[News] = []
        for outlet in outlets:
            article_text = self.generate_news(event, outlet, past_events)
            news_id = generate_id("news")
            news = News(id=news_id, media=outlet.name, article_text=article_text)
            news_list.append(news)
            event.news_article.append(news_id)
        return news_list

    def generate_news(
        self,
        current_event: Event,
        outlet: Media,
        past_events: Optional[List[Event]] = None
    ) -> str:
        """
        사건과 언론사 정보를 바탕으로 뉴스 기사 텍스트를 생성한다.
        반환값은 '본문 텍스트' 하나만.
        """

        # 1) 프롬프트 구성 (이전 사건 → 현재 사건 → 언론사 특성 → 출력 규칙)
        lines = ["다음은 지금까지 발생한 사건들의 요약입니다:\n"]
        if past_events:
            for i, ev in enumerate(past_events[-5:], 1):  # 최근 최대 5개만
                lines.append(
                    f"{i}. 사건명: {ev.event_type} / 카테고리: {ev.category} / "
                    f"감성: {ev.sentiment} / 영향: {ev.impact_level} / 지속: {ev.duration}"
                )
        else:
            lines.append("이전 사건은 없습니다.")

        lines += [
            "\n이후, 현재 사건은 다음과 같습니다:\n",
            "[사건 정보]",
            f"- 제목: {current_event.event_type}",
            f"- 카테고리: {current_event.category}",
            f"- 감성 점수: {current_event.sentiment}",
            f"- 영향 수준: {current_event.impact_level}",
            f"- 지속 기간: {current_event.duration}",
            "",
            "이 사건에 대해, 아래 언론사의 성향과 신뢰도를 반영한 뉴스 기사를 생성하세요:",
            "",
            "[언론사 정보]",
            f"- 이름: {outlet.name}",
            f"- 성향 (bias): {outlet.bias} (-1: 보수, 0: 중립, +1: 진보)",
            f"- 신뢰도 (credibility): {outlet.credibility} (0~1)",
            "",
            "[출력 형식]",
            "뉴스 기사 본문만 출력하세요. 머리말(예: '뉴스 기사:'), 코드블록, 따옴표, 이모지 등은 넣지 마세요.",
            "기사 길이는 250~400자 내외, 한국어로 자연스럽게 작성하세요.",
        ]
        prompt = "\n".join(lines)

        # 2) LLM 호출
        raw = query_llm(prompt).strip()

        # 3) 후처리: 모델이 JSON/라벨/코드펜스를 섞어 줄 가능성 방지
        text = self._extract_news_text(raw)
        text = self._cleanup_text(text)

        return text

    @staticmethod
    def _extract_news_text(raw: str) -> str:
        """
        모델이 실수로 JSON이나 '뉴스 기사:' 같은 라벨을 붙여도
        안전하게 본문만 뽑아내기 위한 보조 루틴.
        """
        # 1) JSON 안에 news_article가 있으면 그걸 사용
        try:
            # JSON 객체/배열 블록만 뽑기
            m_arr = re.search(r"\[\s*\{[\s\S]*?\}\s*\]", raw)
            m_obj = re.search(r"\{[\s\S]*\}", raw) if not m_arr else None
            block = m_arr.group(0) if m_arr else (m_obj.group(0) if m_obj else None)
            if block:
                data = json.loads(block)
                if isinstance(data, dict) and "news_article" in data:
                    return str(data["news_article"])
                if isinstance(data, list) and data and isinstance(data[0], dict) and "news_article" in data[0]:
                    return str(data[0]["news_article"])
        except Exception:
            pass

        # 2) '뉴스 기사:' 라벨 제거
        t = re.sub(r"^\s*뉴스\s*기사\s*:\s*", "", raw, flags=re.IGNORECASE)

        # 3) 코드펜스 제거
        t = re.sub(r"^```[a-zA-Z]*\s*", "", t).strip()
        t = re.sub(r"\s*```$", "", t).strip()

        return t.strip()

    @staticmethod
    def _cleanup_text(text: str) -> str:
        """
        따옴표/이모지/양끝 공백 등 가벼운 정리.
        """
        # 양 끝의 큰따옴표/작은따옴표 제거
        text = text.strip().strip('""""\'')
        # 윈도우 콘솔에서 깨질 수 있는 이모지 제거(선택)
        try:
            text = text.encode("cp949", errors="ignore").decode("cp949")
        except Exception:
            pass
        # 여러 줄 공백 정리
        text = re.sub(r"\n{3,}", "\n\n", text).strip()
        return text

    def _generate_synthetic_events(self, count: int, allowed_categories: Optional[List[str]]) -> List[Event]:
        """LLM이 가용하지 않을 때 사용할 간단한 합성 사건 생성기"""
        categories = allowed_categories or [
            "경제", "정책", "기업", "기술", "국제", "금융", "화학", "에너지", "자동차", "통신"
        ]
        titles = [
            "정부, 산업 지원 정책 발표", "주요 기업 실적 발표", "신기술 상용화 추진", "해외 시장 변동 확대",
            "정책 금리 조정 논의", "대형 M&A 루머", "신규 공장 증설 계획", "규제 완화 방안 검토"
        ]
        durations = ["short", "mid", "long"]
        events: List[Event] = []
        for _ in range(max(1, count)):
            cat = random.choice(categories)
            title = random.choice(titles)
            sentiment = round(random.uniform(-1.0, 1.0), 3)
            impact = random.randint(1, 5)
            duration = random.choice(durations)
            ev = Event(
                id=generate_id("event"),
                event_type=title,
                category=cat,
                sentiment=sentiment,
                impact_level=impact,
                duration=duration,
                news_article=[],
            )
            events.append(ev)
        return events

    def _build_synthetic_article(self, current_event: dict, outlet: Media, recent_events: List[dict]) -> str:
        """LLM이 가용하지 않을 때 사용할 간단한 합성 기사 텍스트 생성기"""
        title = current_event.get("event_type", "시장 동향")
        category = current_event.get("category", "일반")
        tone = "중립"
        if outlet.bias > 0.3:
            tone = "긍정"
        elif outlet.bias < -0.3:
            tone = "신중"
        return (
            f"{title} 관련 소식입니다. {category} 분야에서 주목할 만한 변화가 관측되고 있습니다. "
            f"업계 관계자들은 이번 이슈가 단기적으로 제한적인 영향을 미치겠지만, 중장기적으로는 새로운 기회를 만들 수 있다고 평가합니다. "
            f"기사 작성에는 {outlet.name}의 시각을 반영했으며, 전반적으로 {tone}적 관점에서 내용을 정리했습니다."
        )
