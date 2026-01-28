import json
from domain.ticket_model import Ticket
from services.ticket_service import generate_ticket as _generate_ticket
from renderers.markdown_renderer import to_markdown

def generate_ticket(raw_text: str, module: str, severity: str) -> Ticket:
    return _generate_ticket(raw_text, module, severity)

def make_payloads(ticket: Ticket) -> tuple[str, str, str]:
    md = to_markdown(ticket).strip()
    js = json.dumps(ticket.to_dict(), ensure_ascii=False, indent=2).strip()
    plain = md + "\n\n---\n\n" + js
    return md, js, plain
