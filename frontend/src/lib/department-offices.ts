// 명지전문대학교 각 학과 홈페이지(예: https://mjcs.mjc.ac.kr/)의 페이지
// 하단(footer)에 실제로 게시된 "학과사무실 대표전화"를 2026-08-07에 직접
// 확인해서 정리한 것이다. 없는 정보를 지어내지 않는다는 원칙에 따라, 학과
// 홈페이지에서 전화번호를 찾지 못한 학과는 phone을 null로 둔다:
// - 전자공학과/유아교육학과/자유전공학과: 자체 학과 홈페이지는 있지만
//   페이지에 대표전화가 게시돼 있지 않았다.
// - AI게임소프트웨어학과: mjc.ac.kr 학과안내 목록에 자체 홈페이지 대신
//   네이버 카페(cafe.naver.com/swcontent) 링크만 있어 확인할 방법이 없었다.
// - AI미디어디자인학과: mjc.ac.kr 학과안내 어디에도 자체 홈페이지/서브도메인
//   링크를 찾지 못했다 (비교적 신설 학과로 보임).
//
// "패션·리빙디자인과"는 원문에 "(02)300-300-1236"으로 적혀 있었는데, 다른
// 모든 학과가 예외 없이 "(02)300-XXXX" 형식을 쓰는 걸로 볼 때 "300-"이
// 중복 입력된 오타로 보여 "(02)300-1236"으로 교정했다.
export interface DepartmentOffice {
  department: string;
  phone: string | null;
  office: string | null; // 원문에 방 호수/실습실 등 정보가 있으면 그대로
  homepageUrl: string;
}

export const DEPARTMENT_OFFICES: DepartmentOffice[] = [
  { department: "AI게임소프트웨어학과", phone: null, office: null, homepageUrl: "https://cafe.naver.com/swcontent" },
  { department: "AI미디어디자인학과", phone: null, office: null, homepageUrl: "https://www.mjc.ac.kr/ibuilder.do?menu_idx=100" },
  { department: "컴퓨터공학과", phone: "(02)300-1171", office: null, homepageUrl: "https://mjcs.mjc.ac.kr/" },
  { department: "컴퓨터보안공학과", phone: "(02)300-8737", office: "공학관 808호", homepageUrl: "https://cse.mjc.ac.kr/" },
  { department: "전자공학과", phone: null, office: null, homepageUrl: "https://cee.mjc.ac.kr/" },
  { department: "정보통신공학과", phone: "(02)300-1356", office: "공학관 8층", homepageUrl: "https://itc.mjc.ac.kr/" },
  { department: "기계공학과", phone: "(02)300-1115", office: "공학관 302호", homepageUrl: "https://mee.mjc.ac.kr/" },
  { department: "산업경영공학과", phone: "(02)300-1106", office: "공학관 327호", homepageUrl: "https://idm.mjc.ac.kr/" },
  { department: "전기공학과", phone: "(02)300-1122", office: null, homepageUrl: "https://electrical.mjc.ac.kr/" },
  { department: "토목공학과", phone: "(02)300-1138", office: "공학관 338호", homepageUrl: "https://civil.mjc.ac.kr/" },
  { department: "지적공간정보학과", phone: "(02)300-1145", office: "공학관 330호", homepageUrl: "https://jijuk.mjc.ac.kr/" },
  { department: "드론정보공학과", phone: "(02)300-8750", office: "사회교육관 805호", homepageUrl: "https://droneinfo.mjc.ac.kr/" },
  { department: "경영학과", phone: "(02)300-1152", office: "본관 408호", homepageUrl: "https://ceo.mjc.ac.kr/" },
  { department: "세무회계과", phone: "(02)300-1158", office: "본관 411호", homepageUrl: "https://tax.mjc.ac.kr/" },
  { department: "부동산경영과", phone: "(02)300-1178", office: "본관 413호", homepageUrl: "https://rem.mjc.ac.kr/" },
  { department: "사회복지과", phone: "(02)300-1184", office: "본관 408호", homepageUrl: "https://swd.mjc.ac.kr/" },
  { department: "행정과", phone: "(02)300-1189", office: "본관 417호", homepageUrl: "https://public.mjc.ac.kr/" },
  { department: "공공행정서비스과", phone: "(02)300-1234", office: "본관 3층 318호", homepageUrl: "https://publiccs.mjc.ac.kr/" },
  { department: "영어비즈니스전공", phone: "(02)300-1202", office: "본관 418호", homepageUrl: "https://english.mjc.ac.kr/" },
  { department: "항공서비스과", phone: "(02)300-1202", office: "예체능관 716호", homepageUrl: "https://skysvc.mjc.ac.kr/" },
  { department: "중국어비즈니스과", phone: "(02)300-3843", office: "본관", homepageUrl: "https://china.mjc.ac.kr/" },
  { department: "일본어과", phone: "(02)300-3835", office: "본관 423호", homepageUrl: "https://mjcjp.mjc.ac.kr/" },
  { department: "문예창작과", phone: "(02)300-1224", office: "예체능관 916호", homepageUrl: "https://mjccrw.mjc.ac.kr/" },
  { department: "유아교육학과", phone: null, office: null, homepageUrl: "https://ece.mjc.ac.kr/" },
  { department: "청소년교육상담과", phone: "(02)300-1207", office: "사회교육관 6층", homepageUrl: "https://yde.mjc.ac.kr/" },
  { department: "산업디자인학과", phone: "(02)300-1229", office: "예체능관 617호", homepageUrl: "https://iid.mjc.ac.kr/" },
  { department: "패션·리빙디자인과", phone: "(02)300-1236", office: "Art & Design House 1층 113호", homepageUrl: "https://fashionceramic.mjc.ac.kr/" },
  { department: "커뮤니케이션디자인과", phone: "(02)300-1243", office: null, homepageUrl: "https://mjcd.mjc.ac.kr/" },
  { department: "사회체육과", phone: "(02)300-1219", office: "예체능관 415호", homepageUrl: "https://sls.mjc.ac.kr/" },
  { department: "뷰티매니지먼트과", phone: "(02)300-3640", office: null, homepageUrl: "https://beauty.mjc.ac.kr/" },
  { department: "보건의료정보과", phone: "(02)300-1180", office: "사회교육관 507호", homepageUrl: "https://medinfo.mjc.ac.kr/" },
  { department: "실용음악과", phone: "(02)300-1378", office: "예체능관 816호", homepageUrl: "https://sileum.mjc.ac.kr/" },
  { department: "연극영상학과", phone: "(02)300-1332", office: "본관 816호", homepageUrl: "https://acting.mjc.ac.kr/" },
  { department: "자유전공학과", phone: null, office: null, homepageUrl: "https://cls.mjc.ac.kr/" },
];

// "뷰티매니지먼트과메이크업·네일전공" 같은 세부 전공명은 sugang 학과코드
// 기준이고, 학생이 프로필에 입력하는 department 값과 정확히 일치하지 않을
// 수 있다 - "뷰티매니지먼트과"로 시작하면 같은 학과 사무실로 간주하는 등
// 느슨하게 매칭한다. 완전히 못 찾으면 null.
export function findDepartmentOffice(department: string): DepartmentOffice | null {
  const trimmed = department.trim();
  if (!trimmed) return null;
  return (
    DEPARTMENT_OFFICES.find((d) => d.department === trimmed) ??
    DEPARTMENT_OFFICES.find((d) => trimmed.startsWith(d.department) || d.department.startsWith(trimmed)) ??
    null
  );
}
