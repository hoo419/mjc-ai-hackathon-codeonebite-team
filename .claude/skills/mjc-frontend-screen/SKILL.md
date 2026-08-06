---
name: mjc-frontend-screen
description: Use whenever building or editing a page/screen in this repo's frontend/ (Next.js 16 App Router, MJC AI Campus Agent). Covers the mock-data pattern, shadcn component conventions, and API_CONTRACT.md fidelity that every screen must follow. Trigger on requests like "대시보드 화면 만들어줘", "채팅 페이지 구현", "수강과목 검색 화면 붙여줘", or any DEVELOPER_B_FRONTEND_TASKS.md 담당 화면 작업.
---

# MJC Campus Agent — 프론트 화면 구현 패턴

이 저장소의 `frontend/`는 아직 백엔드가 없다. `API_CONTRACT.md`에 정의된 REST 계약과
동일한 모양의 Mock 데이터로 화면을 먼저 완성하고, 나중에 `lib/api/*.ts`의 내부 구현만
실제 fetch로 바꾸면 되도록 만드는 것이 이 프로젝트 전체의 핵심 설계다. 새 화면을 만들
때마다 이 구조를 깨지 않는 것이 가장 중요하다.

## 이미 있는 것 (다시 만들지 말 것)

- **타입**: `frontend/src/types/index.ts` — `Course`, `Student`, `ScheduleEntry`,
  `ChatResponse`, `EnrollmentResult` 등. `API_CONTRACT.md`와 필드명이 다르면 계약을
  고치는 게 아니라 타입을 계약에 맞춘다 (계약은 개발자 A/B 합의 없이 임의로 바꾸지 않는다).
- **Mock 데이터**: `frontend/src/mocks/*.json`
- **API 클라이언트**: `frontend/src/lib/api/*.ts` — 화면에서 fetch를 직접 하지 말고
  반드시 이 레이어의 함수를 호출한다 (`getCourses`, `enroll`, `sendChatMessage` 등).
- **비동기 데이터 훅**: `frontend/src/hooks/use-async-data.ts` — `useAsyncData(() =>
  getCourses())` 형태로 로딩 상태까지 함께 받는다.
- **한글 라벨/뱃지 매핑**: `frontend/src/lib/labels.ts` — `CourseStatus`,
  `CourseClassType`, `CourseCategory`, `Day` enum을 화면에 그대로(영문 코드로) 노출하지
  않고 이걸 통해서 표시한다.
- **시간표 유틸**: `frontend/src/lib/schedule.ts`, `frontend/src/lib/time.ts` —
  오늘 시간표/다음 수업/시간 충돌 판정은 여기 있는 함수를 재사용한다. 새로 만들지 않는다.
- **레이아웃/네비게이션**: `frontend/src/components/app-shell.tsx` — 이미
  `RootLayout`에 연결되어 있으므로 각 페이지는 네비게이션을 신경 쓸 필요 없이 콘텐츠만
  작성하면 된다.
- **shadcn 컴포넌트**: `frontend/src/components/ui/`에 이미 설치됨(button, card, badge,
  tabs, input, avatar, skeleton, sheet, separator, dialog, alert, scroll-area, select,
  label). 이 프로젝트의 shadcn CLI는 **Base UI**(`@base-ui/react`, `render` prop 방식)를
  쓴다 — Radix `asChild` 패턴이 아니다. 예를 들어 `Button`을 `Link`로 렌더링하려면
  `<Button render={<Link href="/x" />}>라벨</Button>` 처럼 쓴다 (`asChild` prop은
  타입에 없어서 빌드가 깨진다). `components/ui/button.tsx`는 `render`가 있으면 자동으로
  `nativeButton={false}`를 넣도록 이미 고쳐뒀다 — 그렇지 않으면 콘솔에 Base UI native
  button 경고가 뜬다. 새 컴포넌트가 필요하면
  `npx shadcn@latest add <name>`으로 추가하고, 기존 컴포넌트 소스(`ui/dialog.tsx`,
  `ui/sheet.tsx`)를 참고해 `render` prop 패턴을 따른다.

## 새 화면을 만드는 순서

1. `DEVELOPER_B_FRONTEND_TASKS.md`에서 해당 화면의 요구 항목을 확인한다 (표시할 필드,
   버튼, 상태값).
2. 상호작용(검색, 필터, 신청 버튼, 채팅 입력 등)이 있으면 페이지를 `"use client"`로 만들고
   `useAsyncData`로 데이터를 가져온다. 순수 표시 전용이라도 이 프로젝트는 Mock 데이터가
   브라우저 메모리(`lib/api/store.ts`)에 있으므로 클라이언트 컴포넌트로 통일하는 편이
   상태 일관성이 쉽다.
3. 로딩 중에는 `Skeleton`, 실패/빈 상태는 `Alert` 또는 안내 텍스트로 처리한다 — 빈
   화면을 그냥 두지 않는다.
4. 과목/상태 관련 값은 항상 `lib/labels.ts`를 거쳐 한글로 보여준다.
5. 데이터를 변경하는 액션(수강신청 등)은 `lib/api/enrollment.ts`처럼 계약에 정의된 성공/
   실패 코드를 그대로 받아서, 실패 코드별로 사용자에게 다른 안내를 보여준다 — 항상 성공
   하는 것처럼 만들지 않는다.
6. 화면이 실제로 동작하는 걸 `npm run dev`로 눈으로 확인한 뒤 저장소 커밋 규칙
   (`<기능명>: <무엇을 했는지>`)에 맞춰 커밋한다.

## 하지 말 것

- `frontend/` 바깥(`backend/`, `ai/`, `data/`)은 개발자 A 영역이므로 건드리지 않는다.
- `API_CONTRACT.md`의 필드명/Enum/엔드포인트 구조를 화면 편의를 위해 임의로 바꾸지 않는다.
- Next.js 16 기준으로 작업한다 — 학습 데이터에 있는 옛 Next.js 관례(예: 동기 `params`)를
  그대로 쓰지 말고, 필요하면 `frontend/node_modules/next/dist/docs/`를 먼저 확인한다.
