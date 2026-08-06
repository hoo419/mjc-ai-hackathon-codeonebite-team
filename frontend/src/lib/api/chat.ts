import type { ChatResponse } from "@/types";
import { getCourses } from "./courses";
import notices from "@/mocks/notices.json";

// POST /chat — 실제 AI 연결 전까지 키워드 기반 Mock 응답을 반환한다.
export async function sendChatMessage(message: string): Promise<ChatResponse> {
  const q = message.toLowerCase();

  if (q.includes("온라인") && (q.includes("교양") || q.includes("과목"))) {
    const { courses } = await getCourses({ status: "OPEN" });
    const online = courses.filter(
      (c) => c.classType === "ONLINE_LIVE" || c.classType === "ONLINE_RECORDED"
    );
    return {
      answer: "현재 신청 가능한 온라인 과목을 찾았습니다.",
      sources: [{ title: notices[0].title, url: notices[0].url }],
      courses: online,
      actions: online.map((c) => ({ type: "VIEW_COURSE", label: "과목 보기", targetId: c.id })),
    };
  }

  if (q.includes("수강신청") && q.includes("기간")) {
    return {
      answer: "2026학년도 2학기 수강신청 안내 공지를 확인해 주세요.",
      sources: [{ title: notices[0].title, url: notices[0].url }],
    };
  }

  if (q.includes("다음 수업") || q.includes("오늘 수업")) {
    return {
      answer: "시간표 화면에서 오늘/다음 수업을 바로 확인할 수 있습니다.",
      actions: [{ type: "VIEW_COURSE", label: "시간표 보기", targetId: "CS301-01" }],
    };
  }

  return {
    answer: "죄송해요, 아직 Mock 단계라 이 질문에는 정확히 답하기 어려워요. 과목 검색이나 시간표 화면을 참고해 주세요.",
  };
}
