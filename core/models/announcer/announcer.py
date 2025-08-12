from core.models.announcer.prompt_builder import build_prompt
from core.models.announcer.event_schema import Event
import requests
import re
import json

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

        print("[LLM Response Start ↓↓↓]")
        print(output)
        print("[↑↑↑ Response Ended]")

        return self._parse_response(output)


    def _parse_response(self, output: str) -> Event:
        try:
            # 1. JSON 블록 정확히 추출 (가장 바깥 중괄호만)
            json_block_match = re.search(r"\{[\s\S]*\}", output)
            if not json_block_match:
                raise ValueError("JSON 블록을 찾을 수 없습니다.")

            json_str = json_block_match.group(0).strip()

            # 2. (디버깅용) 추출된 JSON 확인
            print("[추출된 JSON]")
            print(json_str)

            # 3. JSON 파싱
            data = json.loads(json_str)

            # 4. Event 객체 생성
            return Event(
                event_type=data["event_type"],
                category=data["category"],
                sentiment=float(data["sentiment"]),
                impact_level=int(data["impact_level"]),
                duration=data["duration"],
                news_article=data["news_article"]
            )

        except Exception as e:
            print("파싱 실패. LLM 응답 전체 ↓↓↓")
            print(output)
            raise e

