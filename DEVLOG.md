# DEVLOG — ai-cs-ticketgen

> CS 문의를 입력하면 개발팀이 바로 착수할 수 있는 “티켓(재현/체크포인트/질문)”으로 정리해주는 Streamlit MVP

---

## 2026-01-28 — MVP 완주 + 유지보수(계층화) 방향 확정

### 목표
- 바이브코딩(LLM 협업)으로 **빠르게 끝까지 완주**하는 경험
- 이후 수정/확장을 위해 **유지보수 친화적인 계층 구조(MVC-ish)로 재구성**
- 결과물을 GitHub에 기록/공유(추후 확장 기반 확보)

### 오늘의 실험 문장
- “CS 문의 원문을 넣으면 개발팀이 바로 착수 가능한 티켓(재현/체크포인트/질문)을 뽑아주는 웹(Streamlit)을 AI와 함께 만든다.”

### 구현한 기능(수직 슬라이스)
- 입력: 모듈, 긴급도, CS 문의 원문
- 처리: 텍스트 정규화/티켓 구조 생성/마크다운·JSON·복사용 텍스트 변환
- 출력: Markdown / JSON / Plain(복사용) 탭 제공

### UI/출력 포맷 개선(반복 수정)
- Markdown 영역:
  - 불필요한 큰 헤더(“[초안] …”로 시작하는 제목) 제거
  - “요약” → “문의사항”으로 명칭 변경
  - “모듈/유형/긴급도”는 시각적으로 더 강조되도록 배치
- Plain(복사용) 영역:
  - 오른쪽이 잘려 보이던 문제 → 줄바꿈/표시 방식 개선

### 장애/트러블슈팅 메모

#### 1) dotenv 모듈 에러
- 증상: `ModuleNotFoundError: No module named 'dotenv'`
- 원인: `streamlit run app.py` 실행이 venv가 아닌 전역 Python을 타는 상황(실행 경로/환경 불일치)
- 해결: `python -m streamlit run app.py` 방식으로 실행 고정

#### 2) MVC-ish 리팩터링 중 services import 에러
- 증상: `ModuleNotFoundError: No module named 'services'`
- 원인: 폴더명 오타/패키지 인식 문제(루트 기준 import 실패)
- 해결: 폴더명 정정 + `__init__.py` 추가 + 실행 확인

#### 3) Git push/pull 충돌(IDE/pycache 추적)
- 원인: `.idea`, `__pycache__`, `.venv` 등이 추적되거나(untracked 상태 포함) 원격과 충돌
- 조치: `.gitignore` 정리 + 추적 해제 + pull/rebase 과정에서 충돌 파일 정리

### 바이브코딩(LLM 협업) 장/단점 정리
- 장점: “상상력 + 요구를 구체화”하면 **개발 속도가 매우 빠름**
- 단점: 수정이 누적되면 결국 **구조/의존성/책임 분리**가 없이는 유지보수가 어려움

### 다음 단계(계획)
- 구조 고정: View(Streamlit) / Controller / Service / Domain / Renderer 분리 강화
- 의존성 방향 고정: View → Controller → Service → Domain, Renderer는 변환만 담당
- MAINTENANCE_MAP을 “변경 유형별 수정 위치 표”로 계속 업데이트
