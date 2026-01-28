import json
import os
from dotenv import load_dotenv

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
  "sanitized": "bool"
}

def normalize_ticket(ticket: dict, module: str, severity: str) -> dict:
    """AI가 스키마를 깨거나 빈값을 줘도, 최소한 '개발 착수' 가능한 형태를 유지하는 안전장치."""
    ticket.setdefault("module", module)
    ticket.setdefault("severity", severity)
    ticket.setdefault("type", "unknown")
    ticket.setdefault("title", "미확인")
    ticket.setdefault("summary", "미확인")
    ticket.setdefault("expected", "미확인")
    ticket.setdefault("actual", "미확인")
    ticket.setdefault("sanitized", True)

    for k in ["repro_steps", "checkpoints", "questions"]:
        v = ticket.get(k)
        if not isinstance(v, list) or len(v) == 0:
            ticket[k] = ["미확인"]

    if len(ticket["repro_steps"]) < 4:
        while len(ticket["repro_steps"]) < 3:
            ticket["repro_steps"].append("미확인")
        ticket["repro_steps"].append("(미확인: 추가정보 필요)")

    raw_hint = (ticket.get("title", "") + " " + ticket.get("summary", "")).lower()

    if ticket["type"] == "unknown":
        if any(x in raw_hint for x in ["오류", "error", "exception", "저장", "크래시", "fail", "실패", "안 됨", "안됨"]):
            ticket["type"] = "bug"
        elif any(x in raw_hint for x in ["통계", "집계", "건수", "데이터", "불일치", "조회값", "값이 다름"]):
            ticket["type"] = "data"
        elif any(x in raw_hint for x in ["개선", "요청", "추가", "성능", "느림", "지연"]):
            ticket["type"] = "request"

    return ticket

def _clean_title_prefix(title: str) -> str:
    """'[초안]' 같이 제목 앞에 붙는 프리픽스를 제거."""
    if not title:
        return "미확인"
    t = title.strip()
    for prefix in ["[초안]", "[초안 ]", "[초안]\u200b"]:
        if t.startswith(prefix):
            t = t[len(prefix):].strip()
    return t or "미확인"

def _mock_ticket(raw_text: str, module: str, severity: str) -> dict:
    txt = raw_text.strip().replace("\r\n", "\n")
    first_line = txt.split("\n")[0][:80] if txt else "미확인"

    ticket = {
        "title": first_line,   # 내부 데이터로는 유지(표시에는 안 씀)
        "module": module,
        "type": "unknown",
        "severity": severity,
        "summary": txt[:500] if txt else "미확인",
        "repro_steps": [
            f"메뉴 진입: {module} 관련 화면으로 이동",
            "대상 기능 선택: 해당 신청서/화면에서 문제 기능 선택",
            "입력/선택 수행: 원문에 언급된 값(예: 해외출장(교육)) 선택",
            "저장/처리 실행: 저장 버튼 클릭 후 결과 확인"
        ],
        "expected": "저장/처리가 정상 완료되어야 함",
        "actual": "오류 발생으로 저장되지 않음(상세 오류/스택은 미확인)",
        "checkpoints": [
            "서버/클라이언트 로그에서 오류 발생 시각 기준으로 스택트레이스 확인",
            "저장 API/프로시저 호출 파라미터 누락 여부 확인",
            "해당 사용자/권한 및 마스터 데이터(코드값) 유효성 점검",
            "DB 트랜잭션/제약조건(Null, FK 등) 위반 여부 확인"
        ],
        "questions": [
            "오류 메시지/스크린샷 또는 로그가 있나요?",
            "특정 사용자만이면 공통점(권한/직급/소속/데이터)이 무엇인가요?",
            "발생 시각/빈도(항상/가끔)는 어떤가요?",
            "다른 브라우저/다른 계정에서도 재현되나요?"
        ],
        "sanitized": True
    }
    return ticket

def generate_ticket(raw_text: str, module: str, severity: str) -> dict:
    mock_mode = os.getenv("MOCK_MODE", "false").lower() == "true"
    api_key = os.getenv("OPENAI_API_KEY", "")

    if mock_mode or not api_key:
        ticket = normalize_ticket(_mock_ticket(raw_text, module, severity), module, severity)
        ticket["title"] = _clean_title_prefix(ticket.get("title", ""))
        return ticket

    from openai import OpenAI
    from prompts import SYSTEM_PROMPT, USER_TEMPLATE

    client = OpenAI(api_key=api_key)

    schema_json = json.dumps(SCHEMA, ensure_ascii=False, indent=2)
    user_prompt = USER_TEMPLATE.format(
        raw_text=raw_text,
        module=module,
        severity=severity,
        schema=schema_json
    )

    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.2,
    )

    content = resp.choices[0].message.content.strip()
    content = content.replace("```json", "").replace("```", "").strip()

    ticket = json.loads(content)
    ticket = normalize_ticket(ticket, module, severity)
    ticket["title"] = _clean_title_prefix(ticket.get("title", ""))
    return ticket

def to_markdown(ticket: dict) -> str:
    """표시용 마크다운 (요청사항 반영)
    - 상단 '제목(H1)' 영역(빨간 박스 텍스트)은 제거
    - 모듈/유형/긴급도는 크게 표시
    - '요약' 대신 '문의사항'
    """
    def li(xs):
        return "\n".join([f"- {x}" for x in xs]) if xs else "- 미확인"

    module = ticket.get("module", "미확인")
    ttype = ticket.get("type", "unknown")
    sev = ticket.get("severity", "medium")

    return f"""# 모듈: {module}
# 유형: {ttype}
# 긴급도: {sev}

## 문의사항
{ticket.get("summary","미확인")}

## 재현 절차
{li(ticket.get("repro_steps", []))}

## 기대 결과
{ticket.get("expected","미확인")}

## 실제 결과
{ticket.get("actual","미확인")}

## 체크포인트
{li(ticket.get("checkpoints", []))}

## 질문
{li(ticket.get("questions", []))}
"""
