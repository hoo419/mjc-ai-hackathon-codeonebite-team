# 개설강좌 실데이터 반영 — 설계 문서

날짜: 2026-08-07
작성자: 개발자A(임채호) + Claude

## 배경
- `data/courses.json`은 지금까지 가짜 18개 과목(Mock)이었다. sugang.mjc.ac.kr에서 실제 개설강좌 246개
  분반(고유)을 이미 수집해 `data/raw/sugang_courses_raw_2026_2.json`에 저장해뒀다 (수집 방법은
  `data/raw/README.md` 참고).
- 사용자가 "sugang 페이지 구조를 완벽하게 베껴서 우리 프로그램을 만들자"고 요청 — 데이터뿐 아니라
  스키마(Course 객체)와 프론트 UI(강좌 조회 화면)까지 실제 사이트 구조에 맞춘다.
- 프론트(`frontend/`)는 원래 개발자B 담당이었으나, 사용자가 "앞으로 모든 작업은 내 담당"이라고 밝혀
  이번 작업 범위에 프론트 변경도 포함한다.

## 목표
1. `data/courses.json`을 실제 246개 분반 데이터로 교체.
2. `CourseCategory` enum을 sugang 원본 이수구분 5종으로 교체.
3. `Course` 객체의 `day`/`startTime`/`endTime`/`building`/`room` 단일 필드를 `sessions` 배열로
   교체 — 한 분반이 여러 요일/시간에 걸치는 걸 있는 그대로 표현 (실제 페이지와 동일한 "한 분반 = 한 로우"
   모델).
4. `classType`은 판단 근거가 있을 때만 채우고, 없으면(원격강좌) 비워둔다 — 근거 없는 값을 지어내지 않는다
   (프로젝트 절대 원칙).
5. `courses` 화면에 실제 사이트처럼 강좌구분/대상학년/학과 드롭다운 + 과목명 검색 필터를 추가한다.

## 비목표 (이번 스펙에서 다루지 않음)
- 실시간 자동 연동(로그인 시 자동으로 최신 개설강좌를 긁어오는 것)은 동일-출처 정책상 불가능 —
  기존 결정 유지, 이번에도 手동 수집한 스냅샷을 쓴다.
- 수강신청 실제 반영(정원/폐강 등)은 여전히 sugang.mjc.ac.kr 몫 — 우리 앱은 "이미 신청한 과목을
  시간표에 기록"만 하는 기존 원칙 유지.
- 지도교수 연락처 표시 기능은 별도 작업(이 스펙과 무관).

## 데이터 스키마

### CourseCategory (교체)
```
GENERAL_COURSE     // 교양과정
GENERAL_REQUIRED   // 교양필수
GENERAL_ELECTIVE   // 일반선택
MAJOR_COURSE       // 전공과정
INTEGRATED_MAJOR   // 통합전공교과
```

### Session (신규)
```json
{ "day": "TUE", "startTime": "13:25", "endTime": "14:50", "building": null, "room": "공502" }
```
- `day`: 기존 `Day` enum(MON~SUN) 그대로 재사용.
- `building`: 항상 `null` — 원본이 "공502" 같은 축약 코드라 정식 건물명을 지어내지 않는다.
- `room`: 원본 문자열 그대로 저장 (가공하지 않음).
- 세션이 없는 과목(시간표 비어있는 특수 과목, 원본에 `"time": " "`인 사례 확인됨)은 `sessions: []`.

### Course (변경)
```json
{
  "id": "T00137-101",
  "name": "딥러닝",
  "professor": "윤현구",
  "credits": 3,
  "category": "MAJOR_COURSE",
  "classType": "OFFLINE",
  "sessions": [
    { "day": "TUE", "startTime": "13:25", "endTime": "14:50", "building": null, "room": "공502" },
    { "day": "WED", "startTime": "10:25", "endTime": "11:50", "building": null, "room": "공502" }
  ],
  "targetGrade": 1,
  "eligibleDepts": [{ "code": "1200203", "name": "컴퓨터공학과" }],
  "capacity": 35,
  "enrolled": 30,
  "status": "OPEN",
  "lastUpdated": "2026-08-07T00:00:00+09:00"
}
```
- `day`/`startTime`/`endTime`/`building`/`room` 필드 **제거**, `sessions` 배열로 대체.
- `targetGrade`/`eligibleDepts` 신규 추가 (계획 단계에서 발견 — 아래 "설계 보완" 참고).
- `classType`: `CourseClassType | None`. 판단 근거: 원본 수집 시 `_sugangGbn`(강좌구분: 10=교양,
  30=전공, 60=원격강좌)이 60이면 `null`(근거 부족), 10/30이면 `"OFFLINE"`.
- `id`: `{원본 subjectCd}-{원본 bunban}` (세션별로 더는 안 쪼갠다 — 한 분반 = 한 Course).

## 변환 파이프라인
1. 원본 `data/raw/sugang_courses_raw_2026_2.json`(246 rows, 원본 API 필드)을 읽는다.
2. 각 row의 `time` 문자열을 `<br>` 기준으로 분리, 각 세션을
   `"{요일} {HH:MM} - {HH:MM} ( {강의실} )"` 정규식으로 파싱해 `sessions[]`로 변환.
   - 빈 문자열(`" "`)이면 `sessions: []`.
   - 요일 한 글자(월화수목금토일) → `Day` enum(MON..SUN) 매핑 테이블 필요.
3. `isuCdNm` → 새 `CourseCategory` 5종 그대로 매핑 (문자열 그대로 enum 값 이름에 대응).
4. `_sugangGbn` → `classType` (60→null, 그 외→OFFLINE).
5. `capacity`=`limitNum`, `enrolled`=`inManNum`, `status`는 `enrolled>=capacity`면 `FULL`
   아니면 `OPEN`.
6. `lastUpdated`는 수집 시각(스크립트 실행 시각, ISO 8601 +09:00)으로 고정.
7. 결과를 `data/courses.json`에 덮어쓴다. 변환 스크립트 자체는 1회성이라 `data/raw/` 옆에 두거나
   `backend/scripts/`에 둔다 (커밋해서 재현 가능하게 남긴다 — Playwright 수집 스크립트와 달리 이건
   외부 의존성이 없는 순수 변환이라 리포에 넣어도 무방).

## 백엔드 변경
- `backend/app/schemas/course.py`: `CourseCategory` 값 교체, `CourseClassType` 관련 필드 nullable,
  `Session` pydantic 모델 추가, `Course.sessions: list[Session]`로 교체, 기존 5개 필드 제거.
- `backend/app/models/course.py`(`CourseModel`, DB 테이블): `sessions`를 JSON 컬럼으로 저장
  (Neon PostgreSQL은 JSONB 지원). 기존 `day/start_time/end_time/building/room` 컬럼 제거.
- `backend/app/repositories/course_repository.py`: `_model_to_schema`에서 JSON 컬럼 ↔ `Session`
  리스트 변환.
- `backend/app/services/enrollment_service.py`: 시간충돌 검사를 "두 과목의 세션 쌍 중 하나라도
  겹치면 충돌"로 확장 (기존엔 단일 day/startTime 비교였음).
- `backend/app/services/chat_service.py`: 과목 검색/응답 생성 시 day/startTime 참조하던 부분을
  세션 배열 기준으로 수정.
- `backend/app/core/seed.py`: DB 시드 로직이 새 스키마로 courses.json을 읽도록 수정.
- 테스트: `test_courses.py`, `test_course_repository.py`(및 enrollment/chat 관련 테스트) 갱신 —
  TDD로 RED(새 스키마 기준 실패하는 테스트 작성) → GREEN 순서로 진행.

## 프론트엔드 변경
- `frontend/src/types/index.ts`: `Course` 타입을 `sessions: Session[]` 구조로, `Day`/새
  `CourseCategory` 값 반영.
- `frontend/src/lib/schedule.ts`: `hasConflict`, `getTodaySchedule`, `getNextClass`를 세션 배열
  기준으로 재작성 (한 과목의 여러 세션 각각을 시간표 엔트리로 펼쳐서 다룸).
- `frontend/src/components/course-card.tsx`: 세션 여러 줄 표시로 변경.
- `frontend/src/lib/labels.ts`: 새 `CourseCategory` 5종 한글 라벨 추가.
- `frontend/src/app/courses/page.tsx`: 강좌구분(교양/전공/원격강좌) · 대상학년(1~4) · 학과(35개,
  `data/raw/dept_codes.json` 재사용 또는 프론트에 하드코딩) 드롭다운 + 과목명 검색 인풋 추가.
  실제 sugang 페이지의 필터 구성을 참고하되, 디자인은 지금 앱의 shadcn 기반 톤을 유지한다
  (표를 그대로 베끼지 않음). UI 다듬기 단계에서 `frontend-design` 스킬 사용.
- `frontend/src/app/schedule/page.tsx`: 시간표 렌더링을 세션 배열 기준으로 수정.

## 테스트 전략
- 백엔드: TDD로 스키마 변환 함수(파서), 시간충돌 검사, repository 매핑을 단위 테스트.
- 변환 스크립트: 246개 원본 row를 실제로 돌려서 파싱 실패(정규식 안 맞는 `time` 형식) 0건인지
  확인하는 걸 완료 기준으로 삼는다.
- 프론트: 최소 `npm run build` 통과 + 주요 화면(`courses`, `schedule`) 수동 확인(`run` 스킬로 앱
  띄워서 스크린샷 확인).

## 브랜치 전략
- `feature/course-data-real` 새 브랜치에서 작업, 완료 후 `integration/fullstack-demo`에 병합.

## 설계 보완 (계획 수립 중 발견)
- 최초 설계엔 없었지만, 프론트에 "대상학년/학과" 드롭다운을 넣으려면 그 데이터가 `Course`에 있어야
  한다는 게 계획 단계에서 드러났다. 원본 재집계 결과 **학년은 분반당 항상 하나**지만, **학과는 246개
  중 21개 분반이 2개 이상 학과에 공통 개방**되어 있었다 (`data/raw/README.md`의 `depts` 필드 참고).
  그래서 `Course`에 다음 두 필드를 추가한다:
  - `targetGrade: number` (1~4)
  - `eligibleDepts: { code: string, name: string }[]` (길이 1 이상)
- "강좌구분"(교양/전공/원격) 필터는 별도 필드를 추가하지 않고 `category`(GENERAL_*/MAJOR_COURSE/
  INTEGRATED_MAJOR) + `classType`(null이면 원격) 조합으로 프론트에서 재구성한다 — 확인 결과 원격강좌는
  `classType: null`로 이미 구분되고, 교양/전공 구분은 `category`로 이미 구분되므로 중복 필드가
  불필요하다.

## 열린 리스크
- `classType`이 원격강좌(60)에서 전부 `null`이 되므로, 프론트 배지 표시가 빈 값을 자연스럽게
  처리해야 한다("확인 안 됨" 문구 등, 지어내지 않는다는 원칙 유지).
- DB 모드(Neon)에서 JSON 컬럼 마이그레이션이 필요 — 기존 데이터가 있다면 마이그레이션 스크립트
  또는 재시딩이 필요할 수 있음 (현재는 Mock 모드가 기본이라 리스크 낮음).
