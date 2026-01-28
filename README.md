유지보수 맵 (CS → Dev Ticket 생성기)
목표
요구사항/버그가 들어왔을 때 “어느 파일을 고치면 되는지”를 30초 안에 찾는다.

1) 프로젝트 계층 구조 (MVC-ish)
View (화면/UI)

app.py
renderers/markdown_renderer.py
Controller (흐름/조립)

controllers/ticket_controller.py
Model/Domain (데이터 구조/정책/품질 하한선)

domain/ticket_model.py
domain/normalizer.py
Service (외부 의존/LLM 호출/Mock)

services/ticket_service.py
Prompt Policy (LLM 정책/스키마)

prompts.py
2) “요구사항 유형”별 수정 위치 바로찾기
A. 화면(UI) 변경
예: 드롭다운 항목 추가/문구 변경/버튼 위치/탭 이름 변경/다운로드 버튼 등

✅ app.py
체크:

“표시만 바뀌는가?” → app.py
“결과 마크다운 텍스트 구조/제목/섹션을 바꾸는가?” → markdown_renderer.py
B. Markdown 출력 포맷 변경 (제목/섹션/순서/라벨)
예: '요약'→'문의사항', 상단 H1 제거, 섹션 순서 변경, 불릿 스타일 변경

✅ renderers/markdown_renderer.py
원칙:

렌더러는 “표현만”
로직/분류/규칙은 절대 넣지 않는다(정책은 normalizer/service 쪽)
C. 티켓 필드 추가/삭제/이름 변경 (데이터 구조 변경)
예: priority 추가, 담당자 추가, tags 추가, 필드명 변경 등

✅ domain/ticket_model.py (Ticket dataclass)
✅ services/ticket_service.py (SCHEMA + from_dict 매핑 영향)
✅ renderers/markdown_renderer.py (출력에 반영할지 여부)
✅ prompts.py (스키마/규칙 업데이트)
팁:

“필드 추가”는 항상 4군데 체크(모델/서비스/프롬프트/렌더러)
D. 분류 규칙 변경 (bug/data/request 판단 기준)
예: “저장 안됨은 bug로 강제”, “문의/가능한지 → request 우선”

✅ domain/normalizer.py (infer_type_from_text)
추가로:

LLM 쪽 분류 정책을 바꾸고 싶으면 prompts.py의 type 분류 규칙도 같이 수정
E. 품질 하한선/정규화 규칙 변경 (누락 보정, 최소 단계 수 등)
예: repro_steps 최소 6단계, checkpoints 최소 5개, '미확인' 처리 개선

✅ domain/normalizer.py (normalize_ticket)
원칙:

LLM이 흔들려도 앱이 무너지지 않게 하는 “최후 방어선”은 여기다.
F. LLM 모델/온도/호출 방식 변경, Mock 동작 변경
예: gpt-4o-mini → 다른 모델, temperature 조정, 응답 파싱 변경, MOCK 개선

✅ services/ticket_service.py
✅ prompts.py (프롬프트 정책 변경 시)
G. .env / 실행환경 / 배포 설정
예: MOCK_MODE 기본값, 키 설정, 실행 옵션 정리

✅ .env / .env.example
✅ requirements.txt / pyproject.toml (의존성 재현)
3) 장애/에러 발생 시 “어디부터 볼지” 디버그 루트
1) import 에러 (ModuleNotFoundError)
폴더명 오타 여부(services 등)
각 폴더에 init.py 존재 여부
실행 커맨드: python -m streamlit run app.py 권장
smoke_test_imports.py로 빠른 점검
2) JSON 파싱 오류 (json.loads 실패)
services/ticket_service.py: LLM 응답 content 확인
prompts.py: “JSON만 출력” 강제 규칙 강화
임시로 MOCK_MODE=true로 전환해 UI만 확인 가능
3) 결과가 이상함 (필드 누락/짧음/미확인 남발)
domain/normalizer.py: 최소 보정 규칙 강화
prompts.py: 질문/체크포인트 생성 규칙 강화
4) 변경 작업 원칙 (유지보수 규율)
표현 변경은 renderer/app에만
정책/규칙 변경은 normalizer/prompt에만
외부 의존(LLM)은 service에만
데이터 구조는 model에만
“한 번의 수정”은 보통 “한 계층”에서 끝나게 설계한다 (필드 추가처럼 구조 변경만 예외)
5) 빠른 리그레션 체크(수정 후 30초)
python smoke_test_imports.py
python -m streamlit run app.py
입력 1개로 Generate → Markdown/JSON/Plain 탭 확인
