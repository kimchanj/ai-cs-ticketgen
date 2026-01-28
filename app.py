import json
import streamlit as st
import streamlit.components.v1 as components

from controllers.ticket_controller import generate_ticket, make_payloads

st.set_page_config(page_title="CS → Dev Ticket", layout="centered")
st.title("CS 문의 → 개발 착수 티켓 생성기 (MVP)")

module = st.selectbox("모듈", ["인사/근태", "원무", "수납", "통계", "권한", "기타"])
severity = st.selectbox("긴급도", ["low", "medium", "high"])
raw = st.text_area("CS 문의 원문", height=220, placeholder="여기에 원문을 붙여넣으세요...")

if st.button("Generate", type="primary", use_container_width=True):
    with st.spinner("티켓 생성 중..."):
        ticket = generate_ticket(raw, module, severity)
        st.session_state["ticket"] = ticket

ticket = st.session_state.get("ticket")
if ticket:
    md, js, plain = make_payloads(ticket)

    tab_md, tab_json, tab_plain = st.tabs(["Markdown", "JSON", "Plain(복사용)"])

    with tab_md:
        st.markdown(md)
        st.download_button(
            "Download .md",
            data=md.encode("utf-8"),
            file_name="ticket.md",
            mime="text/markdown",
            use_container_width=True
        )

    with tab_json:
        st.code(js, language="json")
        st.download_button(
            "Download .json",
            data=js.encode("utf-8"),
            file_name="ticket.json",
            mime="application/json",
            use_container_width=True
        )

    with tab_plain:
        st.caption("아래 영역은 줄바꿈되어 보입니다. 복사는 'Copy to clipboard' 버튼을 누르세요.")
        st.text_area("복사용 텍스트", value=plain, height=420)

        components.html(
            f"""
            <button id="copyBtn" style="padding:10px 14px;border-radius:8px;border:1px solid #ddd;cursor:pointer;">
              Copy to clipboard
            </button>
            <script>
              const btn = document.getElementById("copyBtn");
              btn.addEventListener("click", async () => {{
                try {{
                  await navigator.clipboard.writeText({json.dumps(plain)});
                  btn.innerText = "Copied!";
                  setTimeout(()=>btn.innerText="Copy to clipboard", 1200);
                }} catch(e) {{
                  btn.innerText = "Copy failed";
                  setTimeout(()=>btn.innerText="Copy to clipboard", 1200);
                }}
              }});
            </script>
            """,
            height=60
        )
