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
| `_sugangGbn` | 이 레코드를 수집한 강좌구분 조합 (`10`교양/`30`전공/`60`원격) — 원본 API에는 없고 수집 스크립트가 추가한 메타 필드 |

## Course 스키마로 변환 시 참고할 점 (미착수, 다음 작업자가 결정)
- `time`의 `<br>` 다중 세션을 어떻게 쪼갤지: 세션별로 `id`를 `{subjectCd}-{bunban}-세션번호`로 나눠 여러
  Course row로 만드는 방향으로 지난 논의는 있었으나 최종 확정은 아님.
- `building`/`room`: 원본이 "공706" 같은 축약 코드라 건물 정식명칭을 지어내지 않으려면 `building: null`,
  `room`에 원본 문자열 그대로 넣는 방향으로 논의됐었음 (역시 미확정).
- `category`(MAJOR_REQUIRED 등 API_CONTRACT enum)로 매핑하려면 `isuCdNm` 5종 값과 API_CONTRACT의
  CourseCategory enum(MAJOR_REQUIRED/MAJOR_ELECTIVE/GENERAL_REQUIRED/GENERAL_ELECTIVE/OTHER)을
  대응시켜야 함 — 지금은 안 되어 있음.
- `classType`(OFFLINE/ONLINE_LIVE/ONLINE_RECORDED/HYBRID) 판단 기준(`_sugangGbn===60` 또는 `virYn`)도 미확정.
- API_CONTRACT.md에 없는 필드(분반명/이수구분 원문/학과코드/대상학년 등)를 스키마에 추가할지는
  프론트(개발자B)와 조율 필요 — API_CONTRACT.md부터 고치고 나서 필드를 늘릴 것.

## 수집 스크립트
이 저장소에는 포함하지 않음 (Playwright 등 개발 의존성을 앱에 안 섞으려고 별도 스크래치 폴더에서 실행).
필요하면 다시 요청 시 같은 방식으로 재현 가능.
