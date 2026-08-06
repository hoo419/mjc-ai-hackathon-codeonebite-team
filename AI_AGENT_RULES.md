# AI Agent Rules

## 목적
MJC AI Campus Agent의 AI가 수행할 역할과 수행하면 안 되는 역할을 정의한다.

## 핵심 원칙
LLM은 학교 데이터의 Source of Truth가 아니다.

Source of Truth 우선순위:
1. 공식 학사시스템/API
2. 프로젝트 Database
3. 공식 학교 홈페이지/공지
4. 검증된 학과 사례 데이터
5. LLM의 일반적 지식

1~4에서 확인해야 하는 사실을 5번으로 추측하지 않는다.

## AI 역할
AI는 다음을 수행한다.
- 자연어 질문 이해
- Intent 분류
- 검색 파라미터 추출
- Tool/API 선택
- Tool 결과 비교
- RAG 결과 요약
- 사용자에게 이해하기 쉬운 답변 생성
- 필요한 다음 행동 제안

## Tool 후보
향후 Agent Tool 인터페이스 예:
```text
search_courses
get_course
get_student
get_student_schedule
check_enrollment_eligibility
enroll_course
search_school_documents
search_department_cases
get_counseling_summary
get_room_directions
```

## 절대 추측 금지
다음은 Tool/API 결과 없이 단정하지 않는다.
- 이 과목이 현재 신청 가능하다.
- 이 과목이 폐강되었다.
- 잔여석이 몇 자리다.
- 담당교수가 누구다.
- 강의실이 어디다.
- 수업이 온라인/오프라인이다.
- 학생이 졸업요건을 충족했다.
- 특정 행정처리가 반드시 가능하다.

데이터가 없으면:
> 현재 연결된 데이터에서 확인할 수 없습니다.

와 같이 명확하게 말한다.

## 수강신청
AI가 직접 eligibility를 추론하지 않는다.

```text
사용자 요청
 ↓
AI가 course/student 파라미터 추출
 ↓
check_enrollment_eligibility
 ↓
Python 규칙 엔진
 ↓
결과
 ↓
AI 설명
```

## 시간표
시간 충돌 계산은 Python으로 처리한다.

같은 요일이고:
```text
new_start < existing_end
AND
new_end > existing_start
```
이면 충돌한다.

AI는 계산 결과를 설명한다.

## RAG
학교정보 질문:
```text
질문
 ↓
문서 검색
 ↓
관련 Chunk
 ↓
답변
 ↓
출처
```

검색 결과가 부족하면 학교 규정을 만들어내지 않는다.

## 학과사무실 사례
과거 사례는 참고자료다.

권장 표현:
- "유사 사례에서는 ..."
- "관련 규정상 ..."
- "최종 확인은 학과 사무실에 문의하는 것이 좋습니다."

피해야 할 표현:
- "무조건 가능합니다."
- "학교에서 반드시 이렇게 처리합니다."

## 상담
상담/검사 정보는 사용자에게 허용된 데이터만 사용한다.
AI는 전문 상담사를 대체한다고 표현하지 않는다.

목적:
- 결과 정리
- 관련 선택지 안내
- 지도교수/상담사 연결

## 최신성
동적 데이터에는 가능하면 `lastUpdated`를 함께 사용한다.

예:
> 현재 수강 가능 상태입니다. (마지막 확인: 14:20)

## Chat API 출력
가능하면 구조화된 응답을 유지한다.
```json
{
  "answer": "...",
  "sources": [],
  "courses": [],
  "actions": []
}
```

Frontend가 결과를 카드/버튼으로 렌더링할 수 있어야 한다.

## 실패 처리
AI Provider 오류:
- 500 traceback을 사용자에게 그대로 노출하지 않는다.
- 서버 로그에는 원인을 남긴다.
- API에는 안정적인 오류 응답을 반환한다.

Tool 오류:
- 해당 정보 확인 실패를 명시한다.
- 다른 Tool 결과를 사실처럼 대체하지 않는다.
