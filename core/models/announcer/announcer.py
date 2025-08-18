import json
import re
from typing import List, Optional

from core.models.announcer.event import Event
from core.models.announcer.news import News, Media
from core.models.announcer.prompt_builder import build_event_prompt
from utils.id_generator import generate_id
from llama_client import query_llm  # Ollama/로컬 LLM HTTP 클라이언트 (이미 사용 중)

class Announcer:
    # -----------------------------
    # 사건 생성: LLM → JSON → Event[]
    # -----------------------------
    def generate_events(
        self,
        past_events: Optional[List[Event]] = None,
        count: int = 1,
        allowed_categories: Optional[List[str]] = None
    ) -> List[Event]:
        """
        LLM을 사용해 사건 N개를 생성하여 Event 인스턴스 리스트로 반환합니다.
        - past_events: 맥락에 쓰일 과거 사건들
        - count: 생성할 사건 개수
        - allowed_categories: 허용 카테고리 목록
        """
        prompt = build_event_prompt(
            past_events=past_events,
            count=count,
            allowed_categories=allowed_categories,
            language="ko",
        )
        raw = query_llm(prompt).strip()

        # JSON 블록만 안전 추출
        json_str = self._extract_json_block(raw)
        try:
            data = json.loads(json_str)
        except Exception as e:
            # 혹시 단일 오브젝트로 온 경우(배열이 아니라) 다시 시도
            try:
                data = [json.loads(json_str)]
            except Exception:
                raise ValueError(f"사건 JSON 파싱 실패:\n{raw}") from e

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

    # --------------------------------------------------------
    # 기존 뉴스 생성(이미 구현되어 있는 메서드들) 예시 시그니처
    # --------------------------------------------------------
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

    # ⬇️ announcer.py 내부의 generate_news 메서드 전체를 아래 구현으로 교체하세요.
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

    # ⬇️ announcer.py 안에 아래 헬퍼 2개를 클래스 메서드로 추가하세요.
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
        text = text.strip().strip('“”"\'')
        # 윈도우 콘솔에서 깨질 수 있는 이모지 제거(선택)
        try:
            text = text.encode("cp949", errors="ignore").decode("cp949")
        except Exception:
            pass
        # 여러 줄 공백 정리
        text = re.sub(r"\n{3,}", "\n\n", text).strip()
        return text
