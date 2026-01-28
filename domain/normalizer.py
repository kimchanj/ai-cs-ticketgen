from __future__ import annotations
from typing import Optional
from domain.ticket_model import Ticket

def clean_title_prefix(title: str) -> str:
    if not title:
        return "미확인"
    t = title.strip()
    for prefix in ["[초안]", "[초안 ]", "[초안]\u200b"]:
        if t.startswith(prefix):
            t = t[len(prefix):].strip()
    return t or "미확인"

def infer_type_from_text(text: str) -> str:
    t = (text or "").lower()

    # bug
    if any(x in t for x in ["오류", "error", "exception", "저장", "크래시", "fail", "실패", "안 됨", "안됨", "저장되지"]):
        return "bug"

    # data
    if any(x in t for x in ["통계", "집계", "건수", "데이터", "불일치", "조회값", "값이 다름", "합계"]):
        return "data"

    # request
    if any(x in t for x in ["개선", "요청", "추가", "성능", "느림", "지연", "기능", "문의", "가능한지"]):
        return "request"

    return "unknown"

def normalize_ticket(ticket: Ticket, fallback_module: str, fallback_severity: str) -> Ticket:
    # 기본값/누락 보정
    if not ticket.module or ticket.module == "미확인":
        ticket.module = fallback_module
    if ticket.severity not in ["low", "medium", "high"]:
        ticket.severity = fallback_severity if fallback_severity in ["low", "medium", "high"] else "medium"

    ticket.title = clean_title_prefix(ticket.title or "미확인")
    ticket.summary = ticket.summary or "미확인"
    ticket.expected = ticket.expected or "미확인"
    ticket.actual = ticket.actual or "미확인"
    ticket.sanitized = True if ticket.sanitized is None else bool(ticket.sanitized)

    # 리스트 최소 1개
    if not isinstance(ticket.repro_steps, list) or len(ticket.repro_steps) == 0:
        ticket.repro_steps = ["미확인"]
    if not isinstance(ticket.checkpoints, list) or len(ticket.checkpoints) == 0:
        ticket.checkpoints = ["미확인"]
    if not isinstance(ticket.questions, list) or len(ticket.questions) == 0:
        ticket.questions = ["미확인"]

    # repro_steps 최소 4개
    if len(ticket.repro_steps) < 4:
        while len(ticket.repro_steps) < 3:
            ticket.repro_steps.append("미확인")
        ticket.repro_steps.append("(미확인: 추가정보 필요)")

    # type 최후 보정
    if ticket.type not in ["bug", "data", "request", "unknown"]:
        ticket.type = "unknown"
    if ticket.type == "unknown":
        hint = f"{ticket.title} {ticket.summary}"
        ticket.type = infer_type_from_text(hint)

    return ticket
