# sugang.mjc.ac.kr 개설강좌 원본 수집 데이터 (2026학년 2학기)

`sugang_courses_raw_2026_2.json` — sugang.mjc.ac.kr의 `POST /core/d/lectList` 응답을 그대로 수집해서
과목코드+분반+학기 기준으로 중복만 제거한 **원본(raw) 데이터**입니다. `data/courses.json`(Course 스키마)으로
가공되지 않은 상태이니, 실제 앱에서 쓰려면 `API_CONTRACT.md`의 Course 스키마에 맞게 변환 작업이 필요합니다.

## 수집 방법
- Playwright로 sugang.mjc.ac.kr을 headed 브라우저로 열고, 사용자가 직접 로그인.
- 로그인된 세션에서 `강좌구분(교양10/전공30/원격60) x 대상학년(1~4) x 학과(35개 코드)` 조합으로
  `lectList` API를 순차 호출 (요청 사이 400ms 지연 — 지연 없이 빠르게 연속 호출하면 응답의 한글이
  깨지는 문제가 있었음, 지연을 두니 152개 조합 전부 재시도 없이 정상 수신).
- 메타모포시스(61)는 이번 학기 개설 0건이라 수집 대상에서 제외.
- 원본 981건(같은 과목이 여러 학년/학과 조합에서 중복 노출됨) → `subjectCd+bunban+termCd` 기준
  중복 제거 후 **246개 고유 분반**.

## 필드 설명 (원본 API 응답 그대로, 가공 안 함)
| 필드 | 의미 |
|---|---|
| `subjectCd` | 과목코드 (예: `T00104`) |
| `subjectNmKor` | 과목명 |
| `bunban` | 분반번호 |
| `banNo` | 분반명(특정 학과 전용 반이면 학과명 텍스트, 공통이면 빈 문자열) |
| `nm` | 담당교수명 |
| `credit` | 학점 |
| `isuCdNm` | 이수구분 원문 텍스트 (`교양과정`/`교양필수`/`일반선택`/`전공과정`/`통합전공교과` 5종 확인됨) |
| `isuCd` | 이수구분 코드 |
| `time` | 시간표 문자열. 한 분반이 여러 요일/시간에 걸치면 `<br>`로 여러 세션 구분<br>예: `"수 15:00 - 15:50 ( 공803 ) <br> 수 16:00 - 16:50 ( 공803 )"` — 괄호 안이 강의실(건물+호실 축약코드, 정식 건물명 아님) |
| `grade` / `enterGrade` | 대상학년 |
| `clsMajCd` | 학과코드 (35개 코드는 `data/raw/dept_codes.json` 참고) |
| `limitNum` | 정원 |
| `inManNum` | 신청인원 (사이트 안내상 실시간 아님) |
| `curriYear` / `termCd` | 교육과정 연도 / 학기코드 |
| `virYn` | Y/N — 원격(비대면) 여부로 추정, 확정 매핑은 안 함 |
| `sugangGbnCodes` | 이 분반이 노출된 강좌구분 조합 배열 (`10`교양/`30`전공/`60`원격) — 원본엔 없고 수집 스크립트가 추가. 246개 전부 배열 길이 1 (한 분반은 항상 한 강좌구분에만 속함). |
| `targetGrades` | 이 분반이 노출된 대상학년 배열 — 246개 전부 배열 길이 1 (한 분반=한 학년). |
| `depts` | 이 분반이 노출된 학과 배열 (`{code, name}[]`) — **246개 중 21개는 배열 길이 2 이상** (여러 학과 학생에게 공통 개방된 분반, 주로 통합전공교과). `grade`/`clsMajCd` 원본 필드는 여러 조합 중 마지막으로 관측된 값 하나만 남아있으니 다학과 개방 여부는 반드시 `depts` 배열로 판단할 것. |

## Course 스키마로 변환한 방법 (구현 완료)
실제 변환 로직은 `backend/scripts/transform_sugang_raw.py`를 정본으로 삼는다. 이 원본 JSON을
읽어 `data/courses.json`을 생성하며, 재수집 시 `python -m scripts.transform_sugang_raw`로
다시 실행하면 된다. 결정된 내용:
- `time`의 `<br>` 다중 세션은 한 Course의 `sessions` 배열 원소로 쪼갠다 (row당 별도의 Course를
  만들지 않는다 — `id`는 여전히 `{subjectCd}-{bunban}` 하나). `"원격시험 배정시간"` 세그먼트는
  실제 수업 세션이 아니므로 건너뛴다.
- `building`/`room`: 원본이 "공706" 같은 축약 코드라 건물 정식명칭을 지어내지 않기로 하고
  `building: null`로 고정, `room`에는 원본 문자열을 trim해서 그대로 넣는다 (공백만 있던 값은
  `null`로 정규화 — "알 수 없음"은 빈 문자열이 아니라 `null`이어야 하므로).
- `category`는 `isuCdNm` 원문 5종을 API_CONTRACT의 CourseCategory enum으로 직접 매핑한다:
  `교양과정→GENERAL_COURSE`, `교양필수→GENERAL_REQUIRED`, `일반선택→GENERAL_ELECTIVE`,
  `전공과정→MAJOR_COURSE`, `통합전공교과→INTEGRATED_MAJOR`. (예전에 언급됐던
  `MAJOR_REQUIRED`/`MAJOR_ELECTIVE`/`OTHER` enum 값은 API_CONTRACT.md에서 이미 빠졌고 쓰지 않는다.)
- `classType`은 `sugangGbnCodes[0] == "60"`(원격)이면 `null`, 그 외엔 `"OFFLINE"`으로 판단한다.
  실시간/녹화 구분은 원본에서 알 수 없어 지어내지 않고 전부 `null`로 뭉뚱그린다.
- API_CONTRACT.md에 없던 필드(분반명/이수구분 원문/학과코드 등)는 스키마에 추가하지 않았다 —
  변환은 `id`/`name`/`professor`/`credits`/`category`/`classType`/`sessions`/`targetGrade`/
  `eligibleDepts`/`capacity`/`enrolled`/`status`/`lastUpdated`만 채운다.

## 수집 스크립트
이 저장소에는 포함하지 않음 (Playwright 등 개발 의존성을 앱에 안 섞으려고 별도 스크래치 폴더에서 실행).
필요하면 다시 요청 시 같은 방식으로 재현 가능.
