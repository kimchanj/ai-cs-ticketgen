import json
import os
from dotenv import load_dotenv

from domain.ticket_model import Ticket
from domain.normalizer import normalize_ticket
from prompts import SYSTEM_PROMPT, USER_TEMPLATE

load_dotenv()

SCHEMA = {
    "title": "str",
    "module": "str",
    "type": "bug|data|request|unknown",
    "severity": "low|medium|high",
    "summary": "str",
    "repro_steps": ["str"],
    "expected": "str",
    "actual": "str",
    "checkpoints": ["str"],
    "questions": ["str"],
    "sanitized": "bool",
}

def _mock_ticket(raw_text: str, module: str, severity: str) -> Ticket:
    txt = (raw_text or "").strip().replace("\r\n", "\n")
    first_line = (txt.split("\n")[0][:80] if txt else "미확인")

    t = Ticket(
        title=first_line,
        module=module,
        type="unknown",
        severity=severity if severity in ["low", "medium", "high"] else "medium",
        summary=txt[:500] if txt else "미확인",
        repro_steps=[
            f"메뉴 진입: {module} 관련 화면으로 이동",
            "대상 기능 선택: 해당 신청서/화면에서 문제 기능 선택",
            "입력/선택 수행: 원문에 언급된 값/조건을 선택 또는 입력",
            "저장/처리 실행: 저장/처리 버튼 클릭 후 결과 확인",
        ],
        expected="저장/처리가 정상 완료되어야 함",
        actual="오류/요청 내용으로 인해 기대 동작이 수행되지 않음(상세는 미확인)",
        checkpoints=[
            "서버/클라이언트 로그에서 요청 시각 기준으로 에러/스택트레이스 확인",
            "관련 API/프로시저 호출 파라미터 및 권한 체크",
            "DB 트랜잭션/제약조건(Null, FK 등) 위반 여부 확인",
        ],
        questions=[
            "오류 메시지/스크린샷 또는 로그가 있나요?",
            "발생 시각/빈도(항상/가끔)는 어떤가요?",
            "특정 사용자/특정 조건에서만 재현되나요?",
        ],
        sanitized=True,
    )
    return t

def _call_openai_json(raw_text: str, module: str, severity: str) -> dict:
    # 지연 import(의존성 최소화)
    from openai import OpenAI

    api_key = os.getenv("OPENAI_API_KEY", "")
    client = OpenAI(api_key=api_key)

    schema_json = json.dumps(SCHEMA, ensure_ascii=False, indent=2)
    user_prompt = USER_TEMPLATE.format(
        raw_text=raw_text,
        module=module,
        severity=severity,
        schema=schema_json,
    )

    resp = client.chat.completions.create(
        model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.2,
    )

    content = (resp.choices[0].message.content or "").strip()
    content = content.replace("```json", "").replace("```", "").strip()
    return json.loads(content)

def generate_ticket(raw_text: str, module: str, severity: str) -> Ticket:
    mock_mode = os.getenv("MOCK_MODE", "false").lower() == "true"
    api_key = os.getenv("OPENAI_API_KEY", "")

    if mock_mode or not api_key:
        t = _mock_ticket(raw_text, module, severity)
        return normalize_ticket(t, module, severity)

    d = _call_openai_json(raw_text, module, severity)
    t = Ticket.from_dict(d)
    return normalize_ticket(t, module, severity)
