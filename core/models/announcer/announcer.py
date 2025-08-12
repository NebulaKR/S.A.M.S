from core.models.announcer.prompt_builder import build_prompt
from core.models.announcer.event_schema import Event
import requests
import re

class Announcer:
    def __init__(self, model: str = "llama3", host: str = "http://localhost:11434"):
        self.model = model
        self.api_url = f"{host}/api/generate"

    def generate_event(self, past_events: list[str]) -> Event:
        prompt = build_prompt(past_events)

        response = requests.post(self.api_url, json={
            "model": self.model,
            "prompt": prompt,
            "stream": False
        })
        data = response.json()
        output = data["response"].strip()

        print("[LLM 응답 ↓↓↓]")
        print(output)
        print("[↑↑↑ 응답 끝]")

        return self._parse_response(output)


    def _parse_response(self, output: str) -> Event:
        # 정규식 기반으로 파싱 (간단한 구조화)
        header_match = re.search(r"\[(.*?)\] - (.*?) - ([\-\d\.]+) - (\d) - (\w+)", output)
        article_match = re.search(r"뉴스 기사:\s*(.*)", output, re.DOTALL)

        if not header_match or not article_match:
            raise ValueError("LLM 응답 형식이 예상과 다릅니다")

        event_type, category, sentiment, impact_level, duration = header_match.groups()
        news_article = article_match.group(1).strip()

        return Event(
            event_type=event_type.strip(),
            category=category.strip(),
            sentiment=float(sentiment),
            impact_level=int(impact_level),
            duration=duration.strip(),
            news_article=news_article
        )

