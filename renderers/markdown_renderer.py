from domain.ticket_model import Ticket

def _li(items: list[str]) -> str:
    if not items:
        return "- 미확인"
    return "\n".join([f"- {x}" for x in items])

def to_markdown(ticket: Ticket) -> str:
    return f"""# 모듈: {ticket.module}
# 유형: {ticket.type}
# 긴급도: {ticket.severity}

## 문의사항
{ticket.summary}

## 재현 절차
{_li(ticket.repro_steps)}

## 기대 결과
{ticket.expected}

## 실제 결과
{ticket.actual}

## 체크포인트
{_li(ticket.checkpoints)}

## 질문
{_li(ticket.questions)}
"""
