---
name: mjc-backend-endpoint
description: MJC AI Campus Agent 백엔드에서 API_CONTRACT.md에 정의된 REST 엔드포인트를 새로 구현하거나 수정할 때 사용한다. "학생/시간표/수강신청/채팅/상담/강의실 API 만들어줘", "엔드포인트 추가", "Mock 데이터 기반 API 구현" 같은 요청이면 파일명이나 "스킬"이라는 단어가 없어도 트리거해야 한다. backend/app 엔드포인트(students, enrollment, chat, counseling, buildings, rooms) 작업에 반드시 사용할 것.
---

# MJC Backend Endpoint 구현 절차

`API_CONTRACT.md`가 Frontend/Backend 사이의 유일한 계약이다. 백엔드 쪽에서 계약을 깨거나, 사실 데이터를 LLM이 지어내면 바로 터진다. 그래서 매 엔드포인트마다 아래 순서를 그대로 따른다 — 순서를 건너뛰면 그만큼 나중에 되돌아와서 고치게 된다.

## 0. 시작 전 계약 확인
`API_CONTRACT.md`에서 구현할 엔드포인트의 request/response JSON, 관련 enum, 오류 코드를 정확히 옮겨 적는다. 필드명·enum·엔드포인트 구조는 임의로 바꾸지 않는다. 계약을 바꿔야만 하는 이유가 생기면:
1. 왜 필요한지 설명한다.
2. 승인 후 `API_CONTRACT.md`를 먼저 수정한다.
3. 그 다음 코드를 작성한다.

## 1. TDD로 진행 (superpowers:test-driven-development 병행)
`backend/tests/`에 실패하는 테스트를 먼저 작성한다.
- 성공 케이스: 계약에 정의된 정상 응답 구조와 필드
- 실패 케이스: `API_CONTRACT.md`에 나열된 오류 코드 전부 (예: enrollment의 COURSE_FULL, TIME_CONFLICT, NOT_ELIGIBLE 등)

테스트를 실행해 실제로 실패하는 것을 확인한 뒤에만 구현으로 넘어간다. 실패를 보지 않고 통과하는 테스트는 아무것도 증명하지 않는다.

## 2. 계층 구조를 그대로 지킨다
얇은 라우터 + 순수 서비스 로직으로 나눠야 나중에 Mock → DB 교체가 쉽다.

```
app/schemas/<domain>.py       # Pydantic, API_CONTRACT과 1:1 매칭
app/repositories/<domain>.py  # data/*.json 로드, 순수 함수형 (DB로 교체 가능하게)
app/services/<domain>.py      # 비즈니스 규칙 (아래 3번 참고)
app/api/<domain>.py           # 라우터. 비즈니스 로직을 넣지 않는다.
```

라우터에서 필터링/검증 로직을 직접 하고 있다면 계층이 무너진 것이다 — service로 옮긴다.

## 3. 코드로만 계산해야 하는 것들 (LLM이 절대 추측 금지)
`AI_AGENT_RULES.md` 기준. 아래 값은 반드시 `app/services`의 순수 코드 계산 또는 Mock 데이터 조회 결과여야 한다:
- 잔여석: `remaining = capacity - enrolled`
- 시간 충돌 (같은 요일일 때): `new_start < existing_end AND new_end > existing_start`
- 수강신청 검증 순서: 과목 존재 여부 → 이미 신청했는지 → CANCELLED 여부 → 신청기간/상태 → 정원 → 학생 자격 → 시간 충돌
- 폐강 여부, 신청 가능 여부, 강의실, 수업방식, 담당교수 — 전부 Mock 데이터/코드 결과 그대로 반환

Chat API 같은 LLM 관여 엔드포인트에서는 위 값들을 LLM 프롬프트가 만들어내게 하지 말고, 먼저 서비스 계층에서 계산한 뒤 그 결과를 LLM에게 "설명만" 시킨다. 동적 데이터에는 가능하면 `lastUpdated`를 함께 노출한다.

## 4. 공통 오류 포맷
```json
{ "error": { "code": "COURSE_NOT_FOUND", "message": "..." } }
```
`API_CONTRACT.md`에 정의된 코드 문자열을 그대로 쓴다 (새로 지어내지 않는다).

## 5. 구현 후 체크리스트
- [ ] 관련 테스트 실행 → 전부 통과
- [ ] `uvicorn` 기동 확인 (에러 없이 뜨는지)
- [ ] `/docs` 또는 직접 호출로 응답 JSON을 `API_CONTRACT.md`와 다시 대조
- [ ] import/타입 에러 확인
- [ ] 변경된 파일 목록을 짧게 요약해서 보고

## 6. 경계
- 큰 작업을 한 번에 커밋하지 않는다. `feat: implement <domain> endpoint` 같은 작은 단위 커밋으로 나눈다.
- 진행 중 다음 엔드포인트로 넘어가기 전에, 이번 엔드포인트가 위 체크리스트를 통과했는지 스스로 확인한다.
