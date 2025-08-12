def build_prompt(past_events: list[str]) -> str:
    context = "\n".join(f"{i+1}. {e}" for i, e in enumerate(past_events))
    prompt = f"""
다음은 과거에 발생한 사건들입니다:

{context}

이제, 이어질 수 있는 현실적인 사건을 3개 생성하고, 그에 대한 각각의 뉴스 기사를 작성해주세요.
출력 형식:
[사건명] - [카테고리] - [감성점수] - [영향도(1~5)] - [지속기간(short/mid/long)]
뉴스 기사:
(자연스러운 뉴스 문장)

형식에 맞게 하나만 출력해주세요.
"""
    return prompt.strip()
